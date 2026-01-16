"""Request and response schemas."""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class Document(BaseModel):
    """Document schema."""

    id: str
    content: str
    metadata: Optional[dict] = None
    created_at: datetime = Field(default_factory=datetime.now)


class DocumentCreate(BaseModel):
    """Document creation schema."""

    content: str = Field(..., min_length=1, description="Document content")
    metadata: Optional[dict] = Field(None, description="Optional metadata")


class SearchResult(BaseModel):
    """Search result schema."""

    id: str
    content: str
    score: float
    metadata: Optional[dict] = None


class SearchRequest(BaseModel):
    """Search request schema."""

    query: str = Field(..., min_length=1, description="Search query")
    top_k: Optional[int] = Field(None, ge=1, le=20, description="Number of results")
    score_threshold: Optional[float] = Field(None, ge=0, le=1, description="Minimum score")


class SearchResponse(BaseModel):
    """Search response schema."""

    query: str
    results: List[SearchResult]
    total: int


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    qdrant_connected: bool
    collection_exists: bool
