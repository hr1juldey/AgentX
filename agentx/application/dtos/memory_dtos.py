"""Memory DTOs for REST API.

Pydantic v2 data transfer objects for memory operations.
From C005 memory-rag change.
"""

from typing import Any

from pydantic import BaseModel, Field

from agentx.domain.entities.enums import TemporalType


# Request DTOs


class StoreMemoryRequest(BaseModel):
    """Request to store a memory."""

    content: str = Field(..., min_length=1, description="Memory content")
    userId: str = Field(..., alias="user_id", description="User identifier")
    temporalType: TemporalType = Field(
        default=TemporalType.FACT,
        alias="temporal_type",
        description="Temporal type (auto-classified if not provided)",
    )
    tier: int = Field(default=3, ge=2, le=3, description="Memory tier (2 or 3)")
    sessionId: str | None = Field(
        default=None, alias="session_id", description="Session ID for Tier 2"
    )
    metadata: dict[str, Any] | None = Field(
        default=None, description="Additional metadata"
    )


class SearchMemoryRequest(BaseModel):
    """Request to search memories."""

    query: str = Field(..., min_length=1, description="Search query")
    userId: str = Field(..., alias="user_id", description="User identifier")
    timeFilter: str = Field(
        default="all",
        alias="time_filter",
        description="Time filter (recent, historical, all)",
    )
    tier: int = Field(default=3, ge=2, le=3, description="Memory tier to search")
    sessionId: str | None = Field(
        default=None, alias="session_id", description="Session ID for Tier 2"
    )
    maxResults: int = Field(
        default=10, ge=1, le=100, alias="max_results", description="Maximum results"
    )
    temporalTypes: list[TemporalType] | None = Field(
        default=None, alias="temporal_types", description="Filter by temporal types"
    )


class ConsolidateMemoryRequest(BaseModel):
    """Request to consolidate memories."""

    userId: str = Field(..., alias="user_id", description="User identifier")
    sessionId: str = Field(
        ..., alias="session_id", description="Session to consolidate"
    )
    minMemories: int = Field(
        default=5,
        ge=1,
        alias="min_memories",
        description="Minimum memories required",
    )


# Response DTOs


class SearchResult(BaseModel):
    """Single search result."""

    memoryId: str = Field(..., alias="memory_id", description="Memory ID")
    content: str = Field(..., description="Memory content")
    temporalType: str = Field(..., alias="temporal_type", description="Temporal type")
    createdAt: str = Field(..., alias="created_at", description="Creation timestamp")
    validUntil: str | None = Field(
        default=None, alias="valid_until", description="Expiration if any"
    )
    score: float = Field(..., ge=0, le=1, description="Similarity score")
    superseded: bool = Field(default=False, description="True if outdated")


class SearchMemoryResponse(BaseModel):
    """Response for memory search."""

    results: list[SearchResult] = Field(
        default_factory=list, description="Search results"
    )
    totalFound: int = Field(..., alias="total_found", description="Total results found")
    queryTimeMs: int = Field(..., alias="query_time_ms", description="Query time in ms")


class StoreMemoryResponse(BaseModel):
    """Response for memory storage."""

    memoryId: str = Field(..., alias="memory_id", description="Memory ID")
    content: str = Field(..., description="Memory content")
    userId: str = Field(..., alias="user_id", description="User identifier")
    temporalType: str = Field(..., alias="temporal_type", description="Temporal type")
    createdAt: str = Field(..., alias="created_at", description="Creation timestamp")
    validFrom: str = Field(..., alias="valid_from", description="Valid from timestamp")
    validUntil: str | None = Field(
        default=None, alias="valid_until", description="Expiration"
    )
    tier: int = Field(..., description="Memory tier")
    message: str = Field(..., description="Status message")


class ConsolidateMemoryResponse(BaseModel):
    """Response for memory consolidation."""

    sessionId: str = Field(..., alias="session_id", description="Session ID")
    userId: str = Field(..., alias="user_id", description="User identifier")
    consolidatedAt: str | None = Field(
        default=None, alias="consolidated_at", description="Consolidation timestamp"
    )
    memoriesConsolidated: int = Field(
        ..., alias="memories_consolidated", description="Number consolidated"
    )
    memoriesDiscarded: int = Field(
        ..., alias="memories_discarded", description="Number discarded"
    )
    consolidationSummary: str = Field(
        ..., alias="consolidation_summary", description="Summary message"
    )


# Health check DTOs


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Service status")
    qdrantConnected: bool = Field(
        ..., alias="qdrant_connected", description="Qdrant status"
    )
    timestamp: str = Field(..., description="Current timestamp")
