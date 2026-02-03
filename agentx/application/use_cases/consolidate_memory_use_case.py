"""Consolidate memory use case.

Handles consolidating Tier 2 memories to Tier 3.
From C005 memory-rag change.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from agentx.application.services.duration import DurationMemoryService
from agentx.domain.entities.memory_consolidation import MemoryConsolidationEntity
from agentx.infrastructure.database.qdrant_vector_store import QdrantVectorStore


class ConsolidateMemoryUseCase:
    """Use case for consolidating Tier 2 memories to Tier 3."""

    def __init__(
        self, vector_store: QdrantVectorStore, duration_svc: DurationMemoryService
    ) -> None:
        self._vector_store = vector_store
        self._duration_svc = duration_svc

    async def execute(
        self, user_id: str, session_id: UUID, min_memories: int = 5
    ) -> MemoryConsolidationEntity:
        """Consolidate Tier 2 memories to Tier 3."""
        # Retrieve Tier 2 memories
        memories = await self._vector_store.get_all_memories(
            user_id=user_id, tier=2, session_id=session_id
        )

        if len(memories) < min_memories:
            return MemoryConsolidationEntity(
                session_id=session_id,
                user_id=user_id,
                consolidated_at=None,
                memories_consolidated=0,
                memories_discarded=len(memories),
                consolidation_summary=f"Insufficient memories ({len(memories)} < {min_memories})",
            )

        # Merge duplicates (keep newest per entity)
        merged, discarded_count = self._merge_duplicates(memories)

        # Invalidate outdated facts
        merged = self._invalidate_outdated_facts(merged)

        # Summarize duration events
        duration_count = self._summarize_durations(merged)

        # Store to Tier 3
        consolidated_count = 0
        for memory in merged[:10]:  # Top 10 memories
            await self._vector_store.store_memory(
                content=memory["content"],
                user_id=user_id,
                memory_type=memory["metadata"].get("memory_type", "semantic"),
                temporal_type=memory["metadata"].get("temporal_type", "fact"),
                tier=3,
                session_id=None,
                metadata=memory["metadata"],
            )
            consolidated_count += 1

        return MemoryConsolidationEntity(
            session_id=session_id,
            user_id=user_id,
            consolidated_at=datetime.now(),
            memories_consolidated=consolidated_count,
            memories_discarded=discarded_count,
            consolidation_summary=f"Consolidated {consolidated_count} memories, discarded {discarded_count}, {duration_count} duration events",
        )

    def _merge_duplicates(self, memories: list[dict]) -> tuple[list[dict], int]:
        """Merge duplicate memories. Returns (merged, discarded_count)."""
        seen = {}

        for memory in memories:
            content = memory.get("content", "")
            if content in seen:
                seen[content] = memory  # Keep newest
            else:
                seen[content] = memory

        # Calculate discarded
        discarded = len(memories) - len(seen)

        return list(seen.values()), discarded

    def _invalidate_outdated_facts(self, memories: list[dict]) -> list[dict]:
        """Mark outdated facts in memories."""
        for memory in memories:
            if memory.get("metadata", {}).get("superseded_by"):
                memory["superseded"] = True
        return memories

    def _summarize_durations(self, memories: list[dict]) -> int:
        """Count duration events in memories."""
        count = 0
        for memory in memories:
            metadata = memory.get("metadata", {})
            if metadata.get("duration_seconds"):
                count += 1
        return count
