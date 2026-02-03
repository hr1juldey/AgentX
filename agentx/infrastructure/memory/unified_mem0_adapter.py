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
from agentx.core.memory_config import get_memory_config


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
    - Degraded mode fallback when Qdrant unavailable

    Phase 4 Fix:
    - Uses memory_config for thresholds (Fraud #5.5)
    - Adds degraded mode fallback (Fraud #4.5)
    """

    def __init__(self, enable_degraded_mode: bool = True) -> None:
        """Initialize Mem0AI client with Qdrant and Ollama LLM.

        Args:
            enable_degraded_mode: If True, fall back to local-only mode on Qdrant failure.
                                If False, raise exception on init failure.
        """
        settings = get_settings()
        self._degraded_mode: bool = False
        self._client: Memory | None = None

        try:
            self._client = Memory.from_config(
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
                            "model": settings.llm.model,
                            "ollama_base_url": settings.llm.api_base,
                        },
                    },
                    "history_db_provider": "local",
                }
            )
        except Exception as e:
            if enable_degraded_mode:
                # Fall back to local-only storage (no vector search)
                import logging

                logging.warning(
                    f"Failed to initialize Mem0 with Qdrant at {settings.database.qdrant_url}: {e}. "
                    "Falling back to degraded mode (local-only storage, no semantic search)."
                )
                self._degraded_mode = True
                try:
                    # Try with local-only storage
                    self._client = Memory.from_config(
                        {
                            "vector_store": {"provider": "local"},
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
                except Exception as e2:
                    # Even degraded mode failed, set to None
                    logging.error(
                        f"Failed to initialize Mem0 in degraded mode: {e2}. "
                        "Memory operations will be no-ops."
                    )
                    self._client = None
            else:
                raise RuntimeError(
                    f"Failed to initialize Mem0 with Qdrant at {settings.database.qdrant_url}: {e}"
                ) from e

    @property
    def client(self) -> Memory:
        """Get Mem0 client, raising error if not available."""
        if self._client is None:
            raise RuntimeError("Mem0 client is not available (initialization failed).")
        return self._client

    @property
    def degraded_mode(self) -> bool:
        """Check if adapter is in degraded mode (local-only storage)."""
        return self._degraded_mode

    @property
    def available(self) -> bool:
        """Check if Mem0 client is available."""
        return self._client is not None

    async def store_execution_result(
        self,
        query: str,
        result: str,
        user_id: str,
        confidence: float,
    ) -> bool:
        """Store result ONLY if it meets quality thresholds.

        Prevents hoarding by:
        1. Filtering low-confidence results (< config.quality_threshold)
        2. Filtering trivial results (< config.min_result_length chars)
        3. Checking for duplicates before storing

        Phase 4 Fix: Uses memory_config for thresholds (Fraud #5.5).

        Args:
            query: Original query
            result: Result to store
            user_id: User ID
            confidence: Confidence score (0.0-1.0)

        Returns:
            bool: True if stored, False if filtered
        """
        mem_config = get_memory_config()

        # Filter low-confidence results
        if confidence < mem_config.quality_threshold:
            return False

        # Filter trivial results
        if len(result.strip()) < mem_config.min_result_length:
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
                        memory_id=result.get("id", ""),  # type: ignore[arg-type]
                        content=content,
                        metadata=result.get("metadata", {}),  # type: ignore[arg-type]
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

        Phase 4 Fix: In degraded mode, returns recent memories without semantic search.

        Args:
            query: Search query (ignored in degraded mode)
            user_id: User ID
            limit: Max results

        Returns:
            list[dict]: Search results with correct key names.
        """
        if not self.available:
            return []

        if self._degraded_mode:
            # Degraded mode: return recent memories (no semantic search)
            import logging

            logging.warning(
                "Mem0 in degraded mode - returning recent memories without semantic search"
            )
            # Type: ignore for _client checked by available property
            memories = self._client.get_all(user_id=user_id)  # type: ignore[union-attr]
            results = memories.get("results", [])[:limit]  # type: ignore[index]
            return [
                {
                    "content": r.get("memory", ""),  # type: ignore[attr-defined]
                    "score": 0.0,  # No score in degraded mode
                    "metadata": r.get("metadata", {}),  # type: ignore[attr-defined]
                }
                for r in results
            ]

        # Normal mode: semantic search with Qdrant
        results = self.client.search(query, user_id=user_id, limit=limit)

        return [
            {
                "content": r.get("memory", ""),  # type: ignore[attr-defined]
                "score": r.get("score", 0.0),  # type: ignore[attr-defined]
                "metadata": r.get("metadata", {}),  # type: ignore[attr-defined]
            }
            for r in results
        ]

    async def get_memories(self, user_id: str, limit: int = 10) -> list[dict[str, Any]]:
        """Get memories for a user.

        Phase 4 Fix: Returns empty list if client unavailable.

        Args:
            user_id: User ID
            limit: Max memories to return

        Returns:
            list[dict]: User memories
        """
        if not self.available:
            return []

        memories = self.client.get_all(user_id=user_id)
        return memories.get("results", [])[:limit]  # type: ignore[index]

    async def consolidate_if_needed(self, user_id: str) -> int:
        """Consolidate memories if count exceeds threshold.

        Phase 4 Fix: Uses memory_config for threshold (Fraud #5.5).
        Returns 0 if client unavailable.

        Args:
            user_id: User ID

        Returns:
            int: Number of memories that could be consolidated
        """
        if not self.available:
            return 0

        mem_config = get_memory_config()
        all_memories = self.client.get_all(user_id=user_id)
        memory_count = len(all_memories.get("results", []))  # type: ignore[arg-type]

        if memory_count > mem_config.consolidation_threshold:
            return memory_count - mem_config.consolidation_threshold

        return 0


__all__ = [
    "UnifiedMem0Adapter",
    "ConsolidatedMemory",
]
