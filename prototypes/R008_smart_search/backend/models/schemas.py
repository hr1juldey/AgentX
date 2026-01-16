"""
Request and response schemas for Smart Search API with enhanced Swagger documentation.

This module provides schemas for semantic document search using Qdrant vector database.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class Document(BaseModel):
    """Document schema.

    Represents a searchable document with content and metadata.
    """

    id: str = Field(
        ...,
        description="Unique document identifier (UUID)",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )
    content: str = Field(
        ...,
        description="Document text content (searchable)",
        examples=["This is a document about machine learning..."]
    )
    metadata: Optional[dict] = Field(
        None,
        description="Optional metadata (tags, category, etc.)",
        examples=[{"category": "tech", "tags": ["ai", "ml"]}]
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="When the document was created"
    )


class DocumentCreate(BaseModel):
    """Schema for creating a new document.

    Add a document to the search index.
    """

    content: str = Field(
        ...,
        description="Document text content (will be vectorized)",
        min_length=1,
        examples=["This is a document about machine learning..."]
    )
    metadata: Optional[dict] = Field(
        None,
        description="Optional metadata for filtering",
        examples=[{"category": "tech", "tags": ["ai", "ml"]}]
    )

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "content": "This is a document about machine learning and neural networks...",
                "metadata": {"category": "tech", "tags": ["ai", "ml"]}
            }]
        }
    }


class SearchResult(BaseModel):
    """Schema for a single search result.

    Represents one matching document with relevance score.
    """

    id: str = Field(
        ...,
        description="Document ID",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )
    content: str = Field(
        ...,
        description="Document content (may be truncated)",
        examples=["This is a document about machine..."]
    )
    score: float = Field(
        ...,
        description="Relevance score (0-1, higher is better)",
        examples=[0.92],
        ge=0.0,
        le=1.0
    )
    metadata: Optional[dict] = Field(
        None,
        description="Document metadata"
    )


class SearchRequest(BaseModel):
    """Schema for search request.

    Perform semantic search across indexed documents.
    """

    query: str = Field(
        ...,
        description="Search query (natural language)",
        min_length=1,
        examples=["machine learning papers", "how to optimize neural networks"]
    )
    top_k: Optional[int] = Field(
        None,
        description="Maximum number of results (default: 10)",
        ge=1,
        le=20,
        examples=[5, 10]
    )
    score_threshold: Optional[float] = Field(
        None,
        description="Minimum relevance score (0-1)",
        ge=0.0,
        le=1.0,
        examples=[0.7]
    )

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "query": "machine learning papers",
                "top_k": 10,
                "score_threshold": 0.7
            }]
        }
    }


class SearchResponse(BaseModel):
    """Schema for search response.

    Returns matching documents ranked by relevance.
    """

    query: str = Field(
        ...,
        description="Original search query",
        examples=["machine learning papers"]
    )
    results: List[SearchResult] = Field(
        default_factory=list,
        description="List of matching documents (ranked by score)"
    )
    total: int = Field(
        ...,
        description="Total number of results",
        examples=[42]
    )


class HealthResponse(BaseModel):
    """Schema for health check response.

    Returns service and database connection status.
    """

    status: str = Field(
        ...,
        description="Service health status",
        examples=["healthy", "unhealthy"]
    )
    qdrant_connected: bool = Field(
        ...,
        description="Whether Qdrant vector database is connected",
        examples=[True]
    )
    collection_exists: bool = Field(
        ...,
        description="Whether the search collection exists",
        examples=[True]
    )

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "status": "healthy",
                "qdrant_connected": True,
                "collection_exists": True
            }]
        }
    }


class ErrorResponse(BaseModel):
    """Schema for error response."""

    error: str = Field(
        ...,
        description="Error type",
        examples=["ValidationError", "SearchError"]
    )
    message: str = Field(
        ...,
        description="Error message",
        examples=["Query is required", "Database connection failed"]
    )
    detail: Optional[str] = Field(
        None,
        description="Additional technical details"
    )
