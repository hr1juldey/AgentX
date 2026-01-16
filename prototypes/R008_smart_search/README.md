# R008: Smart Search (Level 4)

Vector-based semantic search prototype using Qdrant and FastEmbed.

## Features

- **Vector Embeddings**: Uses FastEmbed with BAAI/bge-small-en-v1.5 model
- **Semantic Search**: Find similar documents based on meaning, not keywords
- **Qdrant Integration**: Fast vector database for similarity search
- **Document Management**: Index and search through documents

## Tech Stack

- **Backend**: FastAPI + Qdrant + FastEmbed
- **Frontend**: Next.js + shadcn/ui
- **Port**: 8008

## Quick Start

### Backend

```bash
cd backend
pip install -e .
# Start Qdrant first: docker run -p 6333:6333 qdrant/qdrant
python main.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Requirements

- Qdrant running on `localhost:6333`
- Python 3.11+
- Node.js 18+

## API Endpoints

- `POST /documents` - Index a document
- `POST /search` - Semantic search
- `GET /health` - Health check
- `GET /documents/count` - Get document count

## Notes

- First run requires downloading the embedding model (~100MB)
- Qdrant must be running before starting the backend
- Documents are stored in-memory in Qdrant (persisted if using Qdrant Docker)
