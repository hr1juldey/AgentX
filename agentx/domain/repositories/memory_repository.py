"""Memory repository interface.

Abstract base class for memory storage (episodic, semantic, procedural).
Supports multi-hop RAG operations for C005.
"""

from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from agentx.domain.entities.enums import MemoryType


class MemoryRepository(ABC):
    """Repository interface for memory persistence.

    Supports three memory types:
    - Episodic: Conversation history
    - Semantic: Vector embeddings for RAG
    - Procedural: User preferences and patterns
    """

    @abstractmethod
    async def store(
        self,
        memory_type: MemoryType,
        content: str,
        metadata: dict[str, Any],
        session_id: UUID,
    ) -> str:
        """Store a memory entry.

        Args:
            memory_type: Type of memory to store.
            content: Memory content.
            metadata: Additional metadata.
            session_id: Associated session ID.

        Returns:
            str: The memory ID.
        """
        pass

    @abstractmethod
    async def retrieve(
        self, memory_type: MemoryType, query: str, limit: int = 5
    ) -> list[dict[str, Any]]:
        """Retrieve memories by query.

        For semantic memory, performs vector similarity search.
        For episodic memory, retrieves by session/time.
        For procedural memory, retrieves by key.

        Args:
            memory_type: Type of memory to retrieve.
            query: Search query or key.
            limit: Maximum results to return.

        Returns:
            list[dict]: Retrieved memories with metadata.
        """
        pass

    @abstractmethod
    async def retrieve_multi_hop(
        self,
        queries: list[str],
        memory_type: MemoryType = MemoryType.SEMANTIC,
        limit_per_hop: int = 3,
    ) -> list[dict[str, Any]]:
        """Multi-hop RAG retrieval for complex queries.

        Executes multiple retrieval passes and consolidates results.
        Used for agentic RAG operations in C005.

        Args:
            queries: List of queries for each hop.
            memory_type: Type of memory to retrieve.
            limit_per_hop: Results per hop.

        Returns:
            list[dict]: Consolidated retrieval results.
        """
        pass

    @abstractmethod
    async def invalidate(self, memory_id: str, memory_type: MemoryType) -> None:
        """Invalidate a memory entry.

        Used for temporal RAG fact invalidation.

        Args:
            memory_id: The memory ID to invalidate.
            memory_type: Type of memory.
        """
        pass

    @abstractmethod
    async def get_session_history(self, session_id: UUID) -> list[dict[str, Any]]:
        """Get all episodic memories for a session.

        Args:
            session_id: The session identifier.

        Returns:
            list[dict]: Session conversation history.
        """
        pass
