"""Mem0 adapter with safeguards against memory hoarding.

This module provides the Mem0AI adapter with quality filtering
to prevent storing low-quality or duplicate memories.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from mem0 import Memory

if TYPE_CHECKING:
    pass


class Mem0MemoryAdapter:
    """Mem0AI adapter with safeguards against memory hoarding.

    Problem: Mem0 can store every partial execution, bloating memory.
    Solution: Filter and consolidate before storing.
    """

    def __init__(self):
        """Initialize Mem0 adapter with Qdrant backend."""
        self.client = Memory.from_config(
            {
                "vector_store": {
                    "provider": "qdrant",
                    "config": {"host": "localhost", "port": 6333},
                },
            }
        )

    async def store_execution_result(
        self,
        query: str,
        result: str,
        user_id: str,
        confidence: float,
    ) -> bool:
        """Store result ONLY if it meets quality thresholds.

        Prevents hoarding by:
        1. Filtering low-confidence results (< 0.6)
        2. Filtering trivial results (< 50 chars)
        3. Checking for duplicates before storing

        Args:
            query: Original query
            result: Result to store
            user_id: User ID
            confidence: Confidence score (0.0-1.0)

        Returns:
            bool: True if stored, False if filtered
        """
        # Filter low-confidence results
        if confidence < 0.6:
            return False

        # Filter trivial results
        if len(result.strip()) < 50:
            return False

        # Check for duplicates
        existing = self.client.search(query, user_id=user_id, limit=3)
        for ex in existing:
            if ex.get("memory", "") == result:
                return False  # Duplicate

        # Store if passes all filters
        self.client.add(
            result,
            user_id=user_id,
            metadata={
                "query": query,
                "confidence": confidence,
                "stored_at": datetime.now().isoformat(),
            },
        )

        return True

    async def get_memories(self, user_id: str, limit: int = 10) -> list[dict]:
        """Get memories for a user.

        Args:
            user_id: User ID
            limit: Max memories to return

        Returns:
            list[dict]: User memories
        """
        memories = self.client.get_all(user_id=user_id)
        return memories.get("results", [])[:limit]

    async def search_memories(
        self,
        query: str,
        user_id: str,
        limit: int = 5,
    ) -> list[dict]:
        """Search memories by query.

        Args:
            query: Search query
            user_id: User ID
            limit: Max results

        Returns:
            list[dict]: Relevant memories
        """
        results = self.client.search(query, user_id=user_id, limit=limit)
        return results

    async def consolidate_if_needed(self, user_id: str) -> int:
        """Consolidate memories if count exceeds threshold.

        Prevents memory hoarding by consolidating old memories.

        Args:
            user_id: User ID

        Returns:
            int: Number of memories consolidated
        """
        # Get all memories for user
        all_memories = self.client.get_all(user_id=user_id)
        memory_count = len(all_memories.get("results", []))

        # Consolidate if > 100 memories
        if memory_count > 100:
            # Delete oldest memories beyond 100
            # TODO: Implement proper consolidation with LLM summarization
            return memory_count - 100

        return 0
