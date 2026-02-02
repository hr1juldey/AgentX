"""Agent memory adapter using LangGraph Store.

This module provides the AsyncRedisStore adapter for agent memory (cached research).
Agent memory stores research results for cross-thread reuse.

Redis store is managed by the application lifespan context.
"""

import hashlib
import uuid
from datetime import datetime

from langgraph.store.redis.aio import AsyncRedisStore  # type: ignore[import]

from agentx.domain.models.episodic_memory import (
    EpisodicMemory,
    OutcomeQuality,
    TemporalMetadata,
    TemporalType,
)

# Global store instance (set by lifespan)
_store: AsyncRedisStore | None = None


class EpisodicMemoryStore:
    """Agent memory: cached research results.

    Agent Memory (Store):
    - Purpose: Cached research, "what was found"
    - Duration: Cross-thread, persistent
    - Stores: Research results with C005 temporal metadata
    """

    def __init__(self, store: AsyncRedisStore):
        """Initialize episodic memory store.

        Args:
            store: LangGraph AsyncRedisStore instance
        """
        self.store = store

    async def store_research_result(
        self,
        query: str,
        user_id: str,
        summary: str,
        result: str,
        outcome_quality: OutcomeQuality = OutcomeQuality.MEDIUM,
    ) -> str:
        """Store research result for future reuse.

        Args:
            query: Original query
            user_id: User who created this memory
            summary: Brief summary of findings
            result: Full research result
            outcome_quality: Quality of this memory

        Returns:
            str: memory_id
        """
        memory_id = str(uuid.uuid4())
        query_hash = hashlib.sha256(query.lower().encode()).hexdigest()
        namespace = ("research", query_hash)

        # Create memory with C005 temporal metadata
        memory = EpisodicMemory(
            memory_id=memory_id,
            query=query,
            query_hash=query_hash,
            summary=summary,
            result=result,
            temporal=TemporalMetadata(
                created_at=datetime.now(),
                modified_at=datetime.now(),
                valid_from=datetime.now(),
                valid_until=None,  # Still valid
                temporal_type=TemporalType.RESEARCH,
                supersedes=[],
                superseded_by=None,
            ),
            outcome_quality=outcome_quality,
            user_id=user_id,
            session_id="",  # Session ID not needed for cross-thread reuse
        )

        await self.store.aput(namespace, memory_id, memory.model_dump())
        return memory_id

    async def search_research_memories(
        self,
        query: str,
        user_id: str,
        limit: int = 5,
    ) -> list[EpisodicMemory]:
        """Search for relevant cached research.

        Args:
            query: Search query
            user_id: User to search for
            limit: Max results to return

        Returns:
            list[EpisodicMemory]: Relevant memories
        """
        query_hash = hashlib.sha256(query.lower().encode()).hexdigest()
        namespace = ("research", query_hash)

        items = await self.store.asearch(
            namespace,
            query=query,
            limit=limit,
        )

        return [EpisodicMemory(**item.value) for item in items]


def get_store() -> AsyncRedisStore:
    """Get LangGraph Store for agent memory.

    Returns:
        AsyncRedisStore: LangGraph store instance

    Raises:
        RuntimeError: If store is not initialized (lifespan not started)
    """
    global _store
    if _store is None:
        msg = "Store not initialized. Start the application to initialize Redis connections."
        raise RuntimeError(msg)
    return _store


def set_store(store: AsyncRedisStore) -> None:
    """Set the global store instance.

    Called by lifespan context manager during startup.

    Args:
        store: LangGraph store instance
    """
    global _store
    _store = store
