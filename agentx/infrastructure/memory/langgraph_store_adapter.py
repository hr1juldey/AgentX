"""Agent memory adapter using LangGraph Store.

This module provides the PostgresStore adapter for agent memory (cached research).
Agent memory stores research results for cross-thread reuse.
"""

import hashlib
import uuid
from datetime import datetime
from functools import lru_cache

from langgraph.store.postgres import PostgresStore  # type: ignore[import]

from agentx.domain.models.episodic_memory import (
    EpisodicMemory,
    OutcomeQuality,
    TemporalMetadata,
    TemporalType,
)


class EpisodicMemoryStore:
    """Agent memory: cached research results.

    Agent Memory (Store):
    - Purpose: Cached research, "what was found"
    - Duration: Cross-thread, persistent
    - Stores: Research results with C005 temporal metadata
    """

    def __init__(self, store: PostgresStore):
        """Initialize episodic memory store.

        Args:
            store: LangGraph PostgresStore instance
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


@lru_cache
def get_store() -> PostgresStore:
    """Get LangGraph Store for agent memory.

    Returns:
        PostgresStore: LangGraph store instance
    """
    DB_URI = "postgresql://postgres:postgres@localhost:5442/postgres?sslmode=disable"
    return PostgresStore.from_conn_string(DB_URI)
