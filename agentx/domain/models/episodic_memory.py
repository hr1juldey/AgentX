"""Domain models for episodic memory.

This module defines the models for agent memory (Store)
with C005 temporal metadata for fact invalidation.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class TemporalType(str, Enum):
    """Types of temporal memory."""

    RESEARCH = "research"
    CONVERSATION = "conversation"
    FACT = "fact"
    PROCEDURAL = "procedural"


class OutcomeQuality(str, Enum):
    """Quality assessment of memory outcome."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TemporalMetadata(BaseModel):
    """C005 temporal metadata for fact invalidation.

    This metadata supports time-aware RAG with fact invalidation
    based on validity windows and supersession relationships.
    """

    created_at: datetime = Field(description="When this memory was created")
    modified_at: datetime = Field(description="When this memory was last modified")
    valid_from: datetime = Field(description="When this memory becomes valid")
    valid_until: datetime | None = Field(
        default=None,
        description="When this memory expires (None = still valid)",
    )
    temporal_type: TemporalType = Field(description="Type of temporal memory")
    supersedes: list[str] = Field(
        default_factory=list,
        description="IDs of memories this supersedes",
    )
    superseded_by: str | None = Field(
        default=None,
        description="ID of memory that supersedes this",
    )


class EpisodicMemory(BaseModel):
    """Agent memory stored in LangGraph Store (PostgresStore).

    This represents cached research results that can be reused
    across threads for semantically similar queries.
    """

    memory_id: str = Field(description="Unique memory identifier")
    query: str = Field(description="Original query")
    query_hash: str = Field(description="SHA256 hash of query (lowercase)")
    summary: str = Field(description="Brief summary of findings")
    result: str = Field(description="Full research result")

    # C005 temporal metadata
    temporal: TemporalMetadata = Field(description="Temporal metadata for invalidation")

    # Quality tracking
    outcome_quality: OutcomeQuality = Field(
        default=OutcomeQuality.MEDIUM,
        description="Quality of this memory",
    )

    # User association
    user_id: str = Field(description="User who created this memory")
    session_id: str = Field(description="Session where this was created")
