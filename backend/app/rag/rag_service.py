from openai import AsyncOpenAI
from app.rag.vector_store import VectorStore

class RAGService:
    def __init__(self, vector_store: VectorStore, api_key: str, model: str):
        self.store = vector_store
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def answer(self, question: str):
        if self.store.count() == 0:
            return {"answer": "My GitHub knowledge base is empty. Run the ingestion endpoint first.", "sources": []}
        results = self.store.search(question, 6)
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        context = "\n\n---\n\n".join([f"SOURCE: {m.get('source_url')}\nREPOSITORY: {m.get('repo_name')}\nCONTENT:\n{d}" for d, m in zip(docs, metas)])
        system = """You are RepoMind, an AI assistant for a developer portfolio. Answer only from the supplied GitHub context. Never invent projects, technologies, commits, or contributions. If the context is insufficient, say so. Give concise, recruiter-friendly answers. Mention repositories when useful. Do not claim that a technology was used unless supported by the context."""
        response = await self.client.chat.completions.create(model=self.model, temperature=0.2, messages=[{"role":"system","content":system},{"role":"user","content":f"GitHub context:\n\n{context}\n\nQuestion:\n{question}"}])
        unique = []
        seen = set()
        for meta in metas:
            url = meta.get("source_url")
            if url and url not in seen:
                unique.append({"repository": meta.get("repo_name"), "url": url, "type": meta.get("source_type")})
                seen.add(url)
        return {"answer": response.choices[0].message.content or "I couldn't generate an answer.", "sources": unique}
