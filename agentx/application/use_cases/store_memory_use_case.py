"""Store memory use case.

Handles storing memories with temporal metadata enrichment.
From C005 memory-rag change.
"""

from __future__ import annotations

from uuid import UUID

from agentx.application.services.temporal_rag import TemporalRAGService
from agentx.domain.entities.enums import MemoryType, TemporalType
from agentx.infrastructure.database.qdrant_vector_store import QdrantVectorStore


class StoreMemoryUseCase:
    """Use case for storing memories with temporal metadata.

    Enriches memories with temporal classification and metadata
    before storing to Tier 2 or Tier 3.
    """

    def __init__(
        self, vector_store: QdrantVectorStore, temporal_rag: TemporalRAGService
    ) -> None:
        """Initialize store memory use case.

        Args:
            vector_store: Qdrant vector store instance.
            temporal_rag: Temporal RAG service instance.
        """
        self._vector_store = vector_store
        self._temporal_rag = temporal_rag

    async def execute(
        self,
        content: str,
        user_id: str,
        temporal_type: TemporalType | None = None,
        tier: int = 3,
        session_id: UUID | None = None,
        metadata: dict | None = None,
    ) -> dict:
        """Store a memory with temporal metadata enrichment.

        Args:
            content: Memory content.
            user_id: User identifier.
            temporal_type: Optional temporal type (auto-classified if None).
            tier: Memory tier (2 or 3).
            session_id: Session ID for Tier 2.
            metadata: Additional metadata.

        Returns:
            dict: Stored memory with ID and temporal metadata.
        """
        # Add temporal metadata
        temporal_metadata = self._temporal_rag.add_temporal_metadata(
            content, temporal_type
        )

        # Merge with provided metadata
        merged_metadata = {
            **(metadata or {}),
            **temporal_metadata,
        }

        # Store memory
        memory_id = await self._vector_store.store_memory(
            content=content,
            user_id=user_id,
            memory_type=MemoryType.SEMANTIC,
            temporal_type=temporal_metadata["temporal_type"],
            tier=tier,
            session_id=session_id,
            metadata=merged_metadata,
        )

        return {
            "memory_id": str(memory_id),
            "content": content,
            "user_id": user_id,
            "temporal_type": temporal_metadata["temporal_type"].value,
            "created_at": temporal_metadata["created_at"].isoformat(),
            "valid_from": temporal_metadata["valid_from"].isoformat(),
            "valid_until": temporal_metadata["valid_until"],
            "tier": tier,
            "message": "Memory stored successfully",
        }
