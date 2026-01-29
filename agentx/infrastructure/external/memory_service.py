"""Memory and RAG services for Real AgentX v0.1 (C005).

Multi-hop agentic RAG with temporal fact invalidation.
Following memory patterns from docs/research/07_temporal_rag.md.
"""

import time
import uuid
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams, Filter

from agentx.core.config import get_settings
from agentx.domain.entities.enums import MemoryType


class MemoryService:
    """Memory service with episodic, semantic, and procedural storage.

    Supports multi-hop RAG operations and temporal fact invalidation.
    """

    def __init__(self) -> None:
        """Initialize memory service with Qdrant client."""
        settings = get_settings()
        self._qdrant = QdrantClient(url=settings.database.qdrant_url)
        self._collection_name = "agentx_memory"
        self._init_collection()

    def _init_collection(self) -> None:
        """Initialize Qdrant collection if it doesn't exist."""
        collections = self._qdrant.get_collections().collections
        collection_names = [c.name for c in collections]

        if self._collection_name not in collection_names:
            self._qdrant.create_collection(
                collection_name=self._collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE),
            )

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
        memory_id = str(uuid.uuid4())

        # Create embedding (placeholder - would use actual embedding model)
        embedding = self._create_embedding(content)

        # Create point with metadata
        point = PointStruct(
            id=memory_id,
            vector=embedding,
            payload={
                "memory_type": memory_type.value,
                "content": content,
                "session_id": str(session_id),
                "created_at": datetime.now().isoformat(),
                "metadata": metadata,
                "valid_until": (
                    datetime.now() + timedelta(days=7)
                ).isoformat(),  # Temporal invalidation
            },
        )

        self._qdrant.upsert(collection_name=self._collection_name, points=[point])

        return memory_id

    async def retrieve(
        self, memory_type: MemoryType, query: str, limit: int = 5
    ) -> list[dict[str, Any]]:
        """Retrieve memories by query.

        For semantic memory, performs vector similarity search.

        Args:
            memory_type: Type of memory to retrieve.
            query: Search query or key.
            limit: Maximum results to return.

        Returns:
            list[dict]: Retrieved memories with metadata.
        """
        # Create embedding for query
        query_embedding = self._create_embedding(query)

        # Search by memory type
        results = self._qdrant.search(
            collection_name=self._collection_name,
            query_vector=query_embedding,
            query_filter=Filter(
                must=[
                    {
                        "key": "memory_type",
                        "match": {"value": memory_type.value}},
                ]
            ),
            limit=limit,
        )

        # Convert to dict format
        memories = []
        for result in results:
            payload = result.payload
            memories.append(
                {
                    "memory_id": result.id,
                    "content": payload["content"],
                    "session_id": payload["session_id"],
                    "created_at": payload["created_at"],
                    "metadata": payload["metadata"],
                    "score": result.score,
                }
            )

        return memories

    async def retrieve_multi_hop(
        self,
        queries: list[str],
        memory_type: MemoryType = MemoryType.SEMANTIC,
        limit_per_hop: int = 3,
    ) -> list[dict[str, Any]]:
        """Multi-hop RAG retrieval for complex queries.

        Executes multiple retrieval passes and consolidates results.
        Used for agentic RAG operations.

        Args:
            queries: List of queries for each hop.
            memory_type: Type of memory to retrieve.
            limit_per_hop: Results per hop.

        Returns:
            list[dict]: Consolidated retrieval results.
        """
        all_memories = []
        seen_ids = set()

        for query in queries:
            hop_results = await self.retrieve(memory_type, query, limit_per_hop)

            for memory in hop_results:
                # Deduplicate by memory_id
                if memory["memory_id"] not in seen_ids:
                    all_memories.append(memory)
                    seen_ids.add(memory["memory_id"])

        return all_memories

    async def invalidate(self, memory_id: str, memory_type: MemoryType) -> None:
        """Invalidate a memory entry.

        Used for temporal RAG fact invalidation.

        Args:
            memory_id: The memory ID to invalidate.
            memory_type: Type of memory.
        """
        # Mark as invalid by setting valid_until to past
        self._qdrant.set_payload(
            collection_name=self._collection_name,
            payload={("valid_until", datetime.now().isoformat())},
            points=[memory_id],
        )

    async def get_session_history(self, session_id: UUID) -> list[dict[str, Any]]:
        """Get all episodic memories for a session.

        Args:
            session_id: The session identifier.

        Returns:
            list[dict]: Session conversation history.
        """
        # Retrieve episodic memories for session
        results = self._qdrant.scroll(
            collection_name=self._collection_name,
            scroll_filter=Filter(
                must=[
                    {"key": "memory_type", "match": {"value": MemoryType.EPISODIC.value}},
                    {"key": "session_id", "match": {"value": str(session_id)}},
                ]
            ),
            limit=100,
        )

        # Convert to dict format sorted by created_at
        memories = []
        for point in results[0]:
            payload = point.payload
            memories.append(
                {
                    "memory_id": point.id,
                    "content": payload["content"],
                    "created_at": payload["created_at"],
                    "metadata": payload["metadata"],
                }
            )

        # Sort by created_at
        memories.sort(key=lambda m: m["created_at"])
        return memories

    def _create_embedding(self, text: str) -> list[float]:
        """Create embedding for text.

        Args:
            text: Text to embed.

        Returns:
            list[float]: Embedding vector (384-dim placeholder).
        """
        # Placeholder - would use actual embedding model
        # Return zero vector for now
        return [0.0] * 384
