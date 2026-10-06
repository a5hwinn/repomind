from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.ingestion.github_client import GitHubClient
from app.ingestion.github_ingestion import GitHubIngestionService
from app.rag.vector_store import VectorStore
from app.rag.rag_service import RAGService
from app.core.config import get_settings

router = APIRouter()
settings = get_settings()
github = GitHubClient(settings.github_token)
ingestion = GitHubIngestionService(github)
store = VectorStore(settings.chroma_path, settings.openai_api_key, settings.embedding_model)
rag = RAGService(store, settings.openai_api_key, settings.llm_model)

class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)

@router.get("/health")
async def health():
    return {"status": "ok", "documents": store.count()}

@router.post("/ingest")
async def ingest():
    try:
        documents = await ingestion.ingest_user(settings.github_username)
        chunks = store.add_documents(documents)
        return {"status": "success", "repositories_and_documents": len(documents), "indexed_chunks": chunks, "github_username": settings.github_username}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.post("/chat")
async def chat(request: ChatRequest):
    try:
        return await rag.answer(request.question)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
