# =============================================================================
# AGENTX Multi-Hop Search Pydantic Schemas
# =============================================================================
# Pydantic models for API requests/responses and internal data structures
# =============================================================================

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class Citation(BaseModel):
    """A citation from a source document."""

    cited_text: str = Field(..., description="Text cited from the source")
    document_index: int = Field(
        ..., description="Index of the document in search results"
    )
    document_title: str | None = Field(None, description="Title of the document")
    url: str | None = Field(None, description="URL of the source")


class HopEvent(BaseModel):
    """Hop progress event for WebSocket streaming."""

    event_type: str = Field(
        ...,
        description="Event type: hop_start, hop_progress, hop_complete, search_complete",
    )
    hop_number: int = Field(..., description="Current hop number (1-indexed)")
    total_hops: int = Field(..., description="Total number of hops")
    message: str = Field(..., description="Human-readable status message")
    progress: float = Field(..., ge=0.0, le=1.0, description="Progress 0.0 to 1.0")
    eta_seconds: float | None = Field(None, description="Estimated time remaining")
    documents_found: int = Field(default=0, description="Number of documents found")
    query_used: str | None = Field(None, description="Search query used")
    reflection_reasoning: str | None = Field(
        None, description="Runtime reflection output"
    )


class SearchRequest(BaseModel):
    """Search request from client."""

    query: str = Field(..., min_length=1, description="User's search query")
    session_id: str | None = Field(None, description="Optional session identifier")
    max_hops: int | None = Field(
        None, ge=1, le=10, description="Maximum hops (overrides default)"
    )
    enable_citations: bool = Field(
        default=True, description="Include citations in result"
    )


class SearchResult(BaseModel):
    """Final search result."""

    answer: str = Field(..., description="Final synthesized answer")
    citations: list[Citation] = Field(
        default_factory=list, description="Source citations"
    )
    hops: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Details of each hop",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata (time, document counts, etc.)",
    )
    queries_used: list[str] = Field(
        default_factory=list,
        description="All search queries used",
    )
    final_reflection_reasoning: str | None = Field(
        None,
        description="Final reflection on completeness",
    )
