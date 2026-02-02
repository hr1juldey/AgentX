"""Data models for Qdrant vector store.

Defines metadata and configuration models.
"""

from datetime import datetime

from pydantic import BaseModel, Field
from uuid import UUID

from agentx.domain.entities.enums import MemoryType, TemporalType


class MemoryMetadata(BaseModel):
    """Metadata for stored memories.

    Tracks temporal information and memory relationships.
    """

    user_id: str
    session_id: str | None = None
    memory_type: MemoryType
    temporal_type: TemporalType = TemporalType.FACT
    created_at: datetime
    valid_from: datetime
    valid_until: datetime | None = None
    supersedes: list[UUID] = Field(default_factory=list)
    superseded_by: UUID | None = None
