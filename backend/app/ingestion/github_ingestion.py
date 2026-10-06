from app.ingestion.github_client import GitHubClient
from app.models.document import Document

class GitHubIngestionService:
    def __init__(self, github: GitHubClient):
        self.github = github

    async def ingest_user(self, username: str) -> list[Document]:
        repos = await self.github.get_repositories(username)
        documents: list[Document] = []
        for repo in repos:
            name = repo["name"]
            url = repo["html_url"]
            overview = f"""Repository: {name}\nDescription: {repo.get('description') or 'No description'}\nPrimary language: {repo.get('language') or 'Unknown'}\nStars: {repo.get('stargazers_count', 0)}\nForks: {repo.get('forks_count', 0)}\nTopics: {', '.join(repo.get('topics', [])) or 'None'}"""
            documents.append(Document(id=f"repo:{name}", content=overview, source_type="repository", source_url=url, repo_name=name, repo_url=url, metadata={"language": repo.get("language") or "Unknown", "topics": ",".join(repo.get("topics", []))}))

            readme = await self.github.get_readme(username, name)
            if readme:
                documents.append(Document(id=f"readme:{name}", content=readme, source_type="readme", source_url=url, repo_name=name, repo_url=url))

            commits = await self.github.get_commits(username, name)
            for commit in commits:
                sha = commit["sha"]
                commit_data = commit.get("commit", {})
                author = commit_data.get("author") or {}
                content = f"""Repository: {name}\nCommit message: {commit_data.get('message', '')}\nAuthor: {author.get('name', '')}\nDate: {author.get('date', '')}\nSHA: {sha}"""
                documents.append(Document(id=f"commit:{name}:{sha}", content=content, source_type="commit", source_url=commit["html_url"], repo_name=name, repo_url=url, metadata={"sha": sha, "date": author.get("date", "")}))
        return documents
