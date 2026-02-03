"""Mem0AI memory adapter for advanced consolidation.

⚠️ DEPRECATED: This file is deprecated.
Use agentx.infrastructure.memory.unified_mem0_adapter.UnifiedMem0Adapter instead.

This file will be removed in Phase 2 of the memory fraud fixes.
Implements Tier 3 persistent memory with Mem0AI.
From C005 memory-rag change.
"""

from __future__ import annotations

import warnings
from datetime import datetime
from uuid import UUID, uuid4

from mem0 import Memory
from pydantic import BaseModel

from agentx.core.config import get_settings


class ConsolidatedMemory(BaseModel):
    """Consolidated memory from Mem0AI."""

    memory_id: str
    content: str
    metadata: dict
    created_at: datetime


class Mem0MemoryAdapter:
    """Mem0AI adapter for Tier 3 persistent memory.

    Features:
    - Automatic memory summarization
    - Duplicate detection and merging
    - Cross-session persistence
    - Advanced consolidation
    """

    def __init__(self) -> None:
        """Initialize Mem0AI client.

        Note: Mem0AI requires API configuration.
        Falls back to local storage if not configured.

        DEPRECATED: Use UnifiedMem0Adapter instead.
        """
        warnings.warn(
            "Mem0MemoryAdapter from external/mem0_memory.py is deprecated. "
            "Use UnifiedMem0Adapter from infrastructure/memory/unified_mem0_adapter.py instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        settings = get_settings()

        # Initialize Mem0AI
        # Note: For local development, use file-based storage
        # For production, configure Mem0AI cloud
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
                    "history_db_provider": "local",
                }
            )
        except Exception:
            # Fallback to local-only mode
            self.client = Memory()

    async def consolidate_memories(
        self,
        memories: list[dict],
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

            # Add to Mem0AI
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

    async def search_consolidated(
        self, query: str, user_id: str, limit: int = 10
    ) -> list[dict]:
        """Search consolidated memories.

        Args:
            query: Search query.
            user_id: User identifier.
            limit: Maximum results.

        Returns:
            list[dict]: Search results.
        """
        results = self.client.search(query, user_id=user_id, limit=limit)

        return [
            {
                "memory_id": UUID(r.get("id", uuid4())),
                "content": r.get("memory", ""),
                "score": r.get("score", 0.0),
                "metadata": r.get("metadata", {}),
            }
            for r in results
        ]

    async def get_all_consolidated(self, user_id: str) -> list[dict]:
        """Get all consolidated memories for a user.

        Args:
            user_id: User identifier.

        Returns:
            list[dict]: All consolidated memories.
        """
        results = self.client.get_all(user_id=user_id)

        return [
            {
                "memory_id": UUID(r.get("id", uuid4())),
                "content": r.get("memory", ""),
                "metadata": r.get("metadata", {}),
            }
            for r in results
        ]
