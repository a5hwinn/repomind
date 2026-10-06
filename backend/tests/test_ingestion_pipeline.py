import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from app.ingestion.github_client import GitHubClient
from app.ingestion.github_ingestion import GitHubIngestionService
from app.models.document import Document
from app.rag.rag_service import RAGService
from app.rag.vector_store import VectorStore


class MemoryCollection:
    def __init__(self):
        self.items = {}

    def upsert(self, ids, documents, metadatas, embeddings):
        if len(ids) != len(embeddings):
            raise AssertionError("Each indexed chunk must have an embedding")
        for item_id, document, metadata in zip(ids, documents, metadatas):
            self.items[item_id] = {"document": document, "metadata": metadata}

    def get(self, include):
        if include != ["metadatas"]:
            raise AssertionError("Index synchronization should only load metadata")
        return {"ids": list(self.items)}

    def delete(self, ids):
        for item_id in ids:
            self.items.pop(item_id, None)

    def count(self):
        return len(self.items)

    def query(self, query_embeddings, n_results):
        if not query_embeddings:
            raise AssertionError("Search requires an embedding")
        matches = list(self.items.values())[:n_results]
        return {
            "documents": [[item["document"] for item in matches]],
            "metadatas": [[item["metadata"] for item in matches]],
        }


class FakeGitHub:
    async def get_repositories(self, username):
        if not username:
            raise AssertionError("Ingestion should request a GitHub user")
        return [
            {
                "name": "portfolio-project",
                "html_url": "https://github.com/example/portfolio-project",
                "description": "A project to demonstrate portfolio ingestion.",
                "language": "Python",
                "stargazers_count": 3,
                "forks_count": 1,
                "topics": ["portfolio", "machine-learning"],
            }
        ]

    async def get_readme(self, owner, repo):
        if not owner or not repo:
            raise AssertionError("README requests require an owner and repository")
        return "The project uses Python for machine learning."

    async def get_commits(self, owner, repo):
        if not owner or not repo:
            raise AssertionError("Commit requests require an owner and repository")
        return [
            {
                "sha": "abc123",
                "html_url": "https://github.com/example/portfolio-project/commit/abc123",
                "commit": {
                    "message": "Add model evaluation",
                    "author": {"name": "Example", "date": "2026-01-01T00:00:00Z"},
                },
            }
        ]


class FakeChatCompletions:
    def __init__(self):
        self.messages = []

    async def create(self, **kwargs):
        self.messages = kwargs["messages"]
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="Evidence-backed answer."))]
        )


class IngestionPipelineTests(unittest.IsolatedAsyncioTestCase):
    def make_store(self):
        store = VectorStore.__new__(VectorStore)
        store.collection = MemoryCollection()
        store._embed = lambda texts: [[1.0, 0.0] for _ in texts]
        return store

    async def test_github_client_follows_next_page_and_sends_token(self):
        first_page = SimpleNamespace(
            raise_for_status=lambda: None,
            json=lambda: [{"name": "first"}],
            links={"next": {"url": "https://api.github.com/users/example/repos?page=2"}},
        )
        second_page = SimpleNamespace(
            raise_for_status=lambda: None,
            json=lambda: [{"name": "second"}],
            links={},
        )
        client = AsyncMock()
        client.__aenter__.return_value = client
        client.__aexit__.return_value = None
        client.get.side_effect = [first_page, second_page]

        with patch("app.ingestion.github_client.httpx.AsyncClient", return_value=client):
            github = GitHubClient("unit-test-token")
            repositories = await github.get_repositories("example")

        self.assertEqual([repo["name"] for repo in repositories], ["first", "second"])
        self.assertIn("unit-test-token", github.headers["Authorization"])
        self.assertEqual(client.get.await_count, 2)
        self.assertEqual(client.get.await_args_list[0].kwargs["params"]["per_page"], 100)
        self.assertIsNone(client.get.await_args_list[1].kwargs["params"])

    async def test_ingestion_to_chat_returns_indexed_source_links(self):
        service = GitHubIngestionService(FakeGitHub())
        store = self.make_store()
        documents = await service.ingest_user("example")

        self.assertEqual(len(documents), 3)
        indexed_chunks = store.add_documents(documents)
        self.assertEqual(indexed_chunks, 3)

        rag = RAGService.__new__(RAGService)
        rag.store = store
        rag.model = "test-model"
        chat = FakeChatCompletions()
        rag.client = SimpleNamespace(
            chat=SimpleNamespace(completions=chat)
        )
        result = await rag.answer("What does the project use?")

        self.assertEqual(result["answer"], "Evidence-backed answer.")
        self.assertIn("uses Python for machine learning", chat.messages[1]["content"])
        self.assertIn("Add model evaluation", chat.messages[1]["content"])
        self.assertEqual(
            {source["url"] for source in result["sources"]},
            {
                "https://github.com/example/portfolio-project",
                "https://github.com/example/portfolio-project/commit/abc123",
            },
        )

    async def test_failed_commit_fetch_aborts_ingestion(self):
        github = FakeGitHub()

        async def fail_to_fetch_commits(owner, repo):
            raise RuntimeError(f"GitHub commits endpoint unavailable for {owner}/{repo}")

        github.get_commits = fail_to_fetch_commits
        service = GitHubIngestionService(github)

        with self.assertRaisesRegex(RuntimeError, "commits endpoint unavailable"):
            await service.ingest_user("example")

    def test_reindex_removes_old_chunks_and_deleted_repositories(self):
        store = self.make_store()
        old_documents = [
            Document(
                id="repo:old-project",
                content="old " * 500,
                source_type="repository",
                source_url="https://github.com/example/old-project",
                repo_name="old-project",
                repo_url="https://github.com/example/old-project",
            )
        ]
        current_documents = [
            Document(
                id="repo:current-project",
                content="Current project.",
                source_type="repository",
                source_url="https://github.com/example/current-project",
                repo_name="current-project",
                repo_url="https://github.com/example/current-project",
            )
        ]

        old_count = store.add_documents(old_documents)
        self.assertGreater(old_count, 1)

        current_count = store.add_documents(current_documents)

        self.assertEqual(current_count, 1)
        self.assertEqual(store.count(), 1)
        self.assertEqual(
            list(store.collection.items),
            ["repo:current-project:chunk:0"],
        )


if __name__ == "__main__":
    unittest.main()
