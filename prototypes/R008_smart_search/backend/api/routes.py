"""API routes."""

from fastapi import APIRouter, HTTPException

from models.schemas import (
    Document,
    DocumentCreate,
    HealthResponse,
    SearchRequest,
    SearchResponse,
)
from services.service import search_service

router = APIRouter(tags=["search"])


@router.post("/documents", response_model=Document)
async def add_document(document: DocumentCreate):
    """Add a document to the search index."""
    doc_id = await search_service.add_document(document)

    if doc_id is None:
        raise HTTPException(
            status_code=503,
            detail="Search service unavailable. Please ensure Qdrant is running."
        )

    return Document(id=doc_id, content=document.content, metadata=document.metadata)


@router.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """Search for similar documents."""
    results = await search_service.search(request)

    return SearchResponse(
        query=request.query,
        results=results,
        total=len(results)
    )


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    info = await search_service.get_collection_info()

    return HealthResponse(
        status="healthy" if info["connected"] else "unhealthy",
        qdrant_connected=info["connected"],
        collection_exists=info["collection_exists"]
    )


@router.get("/documents/count")
async def get_document_count():
    """Get the number of indexed documents."""
    info = await search_service.get_collection_info()
    return {"count": info["document_count"]}
