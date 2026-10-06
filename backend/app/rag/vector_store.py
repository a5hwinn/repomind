import chromadb
from openai import OpenAI
from app.models.document import Document
from app.rag.chunker import chunk_text

class VectorStore:
    def __init__(self, path: str, api_key: str, embedding_model: str):
        self.client = chromadb.PersistentClient(path=path)
        self.collection = self.client.get_or_create_collection(name="repomind")
        self.openai = OpenAI(api_key=api_key)
        self.embedding_model = embedding_model

    def _embed(self, texts: list[str]) -> list[list[float]]:
        result = self.openai.embeddings.create(model=self.embedding_model, input=texts)
        return [item.embedding for item in result.data]

    def add_documents(self, documents: list[Document]):
        ids, texts, metas = [], [], []
        for doc in documents:
            for index, chunk in enumerate(chunk_text(doc.content)):
                ids.append(f"{doc.id}:chunk:{index}")
                texts.append(chunk)
                metas.append({"source_type": doc.source_type, "source_url": doc.source_url, "repo_name": doc.repo_name, "repo_url": doc.repo_url, **{k: str(v) for k, v in doc.metadata.items()}})
        for start in range(0, len(texts), 64):
            batch_texts = texts[start:start+64]
            batch_ids = ids[start:start+64]
            batch_metas = metas[start:start+64]
            embeddings = self._embed(batch_texts)
            self.collection.upsert(ids=batch_ids, documents=batch_texts, metadatas=batch_metas, embeddings=embeddings)

        existing_ids = set(self.collection.get(include=["metadatas"])["ids"])
        stale_ids = existing_ids.difference(ids)
        if stale_ids:
            self.collection.delete(ids=list(stale_ids))

        return len(texts)

    def search(self, query: str, n_results: int = 6):
        embedding = self._embed([query])[0]
        return self.collection.query(query_embeddings=[embedding], n_results=n_results)

    def count(self):
        return self.collection.count()
