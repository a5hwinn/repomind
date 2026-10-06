# RepoMind

RepoMind is an AI-aware developer portfolio that ingests your GitHub repositories, READMEs, and commit history and lets visitors ask grounded questions about your work.

## MVP

- GitHub repository + README + commit ingestion
- OpenAI embeddings
- ChromaDB vector store
- RAG chat API
- Source links in answers
- Next.js portfolio UI
- Docker Compose setup

## Quick start

### 1. Configure

Copy `.env.example` to `.env` and add your OpenAI API key. Set `GITHUB_USERNAME` to your GitHub username. A GitHub token is optional but recommended for higher API limits.

### 2. Run with Docker

```bash
docker compose up --build
```

Open http://localhost:3000.

### 3. Ingest GitHub

From another terminal:

```bash
curl -X POST http://localhost:8000/ingest
```

Then ask questions from the portfolio.

### Local development

Backend:

```bash
cd backend
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
cd ..
backend\\.venv\\Scripts\\uvicorn.exe app.main:app --app-dir backend --reload --port 8000
```

Run the backend ingestion tests from the `backend` directory:

```bash
cd backend
.venv\\Scripts\\python.exe -m unittest discover -s tests -v
```

Each successful ingestion reads every page of the owned repositories and their commit histories, then synchronizes the local vector index to that snapshot. Repositories or chunks no longer present are removed. If GitHub ingestion fails, the existing index is left in place and the API reports the failure.

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## Project structure

```text
backend/   FastAPI, GitHub ingestion, embeddings, RAG
frontend/  Next.js portfolio
```

## Notes

The first MVP intentionally avoids heavyweight agent frameworks. The architecture is simple and inspectable: GitHub -> documents -> chunks -> embeddings -> ChromaDB -> retrieval -> LLM.
