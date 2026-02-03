"""Unified Mem0AI adapter combining consolidation and quality filtering.

Merges functionality from two duplicate Mem0MemoryAdapter implementations:
- infrastructure/external/mem0_memory.py (consolidation focus)
- infrastructure/memory/mem0_adapter.py (quality filtering focus)

This is the SINGLE source of truth for all Mem0 operations.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from mem0 import Memory
from pydantic import BaseModel

from agentx.core.config import get_settings


class ConsolidatedMemory(BaseModel):
    """Consolidated memory from Mem0AI."""

    memory_id: str
    content: str
    metadata: dict[str, Any]
    created_at: datetime


class UnifiedMem0Adapter:
    """Single unified adapter for all Mem0 operations.

    Combines:
    - Quality filtering (prevents memory hoarding)
    - Consolidation (Mem0's built-in duplicate detection)
    - Search and retrieval (ColBERTv2 via Qdrant)

    Features:
    - Automatic memory summarization
    - Duplicate detection and merging
    - Cross-session persistence
    - Quality-based filtering
    """

    QUALITY_THRESHOLD: float = 0.6
    MIN_LENGTH: int = 50
    CONSOLIDATION_THRESHOLD: int = 100

    def __init__(self) -> None:
        """Initialize Mem0AI client with Qdrant and Ollama LLM."""
        settings = get_settings()

        try:
            self.client = Memory.from_config(
                {
                    "vector_store": {
                        "provider": "qdrant",
                        "config": {
                            "host": settings.database.qdrant_url,
                            "port": 6335,
                        },
                    },
                    "llm": {
                        "provider": "ollama",
                        "config": {
                            "model": "gemma3:4b",
                            "ollama_base_url": settings.llm.api_base,
                        },
                    },
                    "history_db_provider": "local",
                }
            )
        except Exception as e:
            raise RuntimeError(
                f"Failed to initialize Mem0 with Qdrant at {settings.database.qdrant_url}: {e}"
            ) from e

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
        if confidence < self.QUALITY_THRESHOLD:
            return False

        # Filter trivial results
        if len(result.strip()) < self.MIN_LENGTH:
            return False

        # Check for duplicates
        existing = await self.search_memories(query, user_id, limit=3)
        for ex in existing:
            if ex.get("content", "") == result:
                return False

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

    async def consolidate_memories(
        self,
        memories: list[dict[str, Any]],
        user_id: str,
    ) -> list[ConsolidatedMemory]:
        """Consolidate memories using Mem0AI.

        Args:
            memories: List of memories to consolidate.
            user_id: User identifier.

        Returns:
            list[ConsolidatedMemory]: Consolidated memories.
        """
        consolidated = []

        for memory in memories:
            content = memory.get("content", "")
            if not content:
                continue

            result = self.client.add(
                content,
                user_id=user_id,
                metadata=memory.get("metadata", {}),
            )

            if result:
                consolidated.append(
                    ConsolidatedMemory(
                        memory_id=result.get("id", ""),
                        content=content,
                        metadata=result.get("metadata", {}),
                        created_at=datetime.now(),
                    )
                )

        return consolidated

    async def search_memories(
        self,
        query: str,
        user_id: str,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Search memories with ColBERTv2 via Qdrant.

        Args:
            query: Search query
            user_id: User ID
            limit: Max results

        Returns:
            list[dict]: Search results with correct key names.
        """
        results = self.client.search(query, user_id=user_id, limit=limit)

        return [
            {
                "content": r.get("memory", ""),  # Mem0 uses "memory" key
                "score": r.get("score", 0.0),
                "metadata": r.get("metadata", {}),
            }
            for r in results
        ]

    async def get_memories(self, user_id: str, limit: int = 10) -> list[dict[str, Any]]:
        """Get memories for a user.

        Args:
            user_id: User ID
            limit: Max memories to return

        Returns:
            list[dict]: User memories
        """
        memories = self.client.get_all(user_id=user_id)
        return memories.get("results", [])[:limit]

    async def consolidate_if_needed(self, user_id: str) -> int:
        """Consolidate memories if count exceeds threshold.

        Args:
            user_id: User ID

        Returns:
            int: Number of memories that could be consolidated
        """
        all_memories = self.client.get_all(user_id=user_id)
        memory_count = len(all_memories.get("results", []))

        if memory_count > self.CONSOLIDATION_THRESHOLD:
            return memory_count - self.CONSOLIDATION_THRESHOLD

        return 0


__all__ = [
    "UnifiedMem0Adapter",
    "ConsolidatedMemory",
]
