"""Qdrant vector store adapter for memory storage.

Implements Tier 2 (session-scoped) and Tier 3 (persistent) memory.
From C005 memory-rag change.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from fastembed import LateInteractionTextEmbedding
from pydantic import BaseModel, Field
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    MultiVectorComparator,
    MultiVectorConfig,
    PointStruct,
    VectorParams,
)

from agentx.core.config import get_settings
from agentx.core.memory_config import get_memory_config
from agentx.domain.entities.enums import MemoryType, TemporalType


class MemoryMetadata(BaseModel):
    """Metadata for stored memories."""

    user_id: str
    session_id: str | None = None
    memory_type: MemoryType
    temporal_type: TemporalType = TemporalType.FACT
    created_at: datetime
    valid_from: datetime
    valid_until: datetime | None = None
    supersedes: list[UUID] = Field(default_factory=list)
    superseded_by: UUID | None = None


class QdrantVectorStore:
    """Qdrant adapter for ColBERT multivector storage.

    Supports:
    - Tier 2: Session-scoped memories (ephemeral)
    - Tier 3: Persistent long-term memories
    - Temporal metadata (created_at, valid_until, supersedes)
    """

    def __init__(self) -> None:
        """Initialize Qdrant client and ColBERT embedder."""
        settings = get_settings()
        memory_config = get_memory_config()

        self.client = QdrantClient(url=settings.database.qdrant_url)
        self.memory_config = memory_config
        self._embedder: LateInteractionTextEmbedding | None = None

    @property
    def embedder(self) -> LateInteractionTextEmbedding:
        """Lazy-load ColBERT embedder.

        Returns:
            LateInteractionTextEmbedding: ColBERT embedder instance.
        """
        if self._embedder is None:
            self._embedder = LateInteractionTextEmbedding(
                self.memory_config.colbert_model_name
            )
        return self._embedder

    def _get_collection_name(
        self, user_id: str, tier: int = 3, session_id: UUID | None = None
    ) -> str:
        """Get collection name for tier and user.

        Args:
            user_id: User identifier.
            tier: Memory tier (2 or 3).
            session_id: Session ID for Tier 2.

        Returns:
            str: Collection name.
        """
        if tier == 2 and session_id:
            return f"{self.memory_config.tier2_collection_prefix}{user_id}_session_{session_id}"
        return f"{self.memory_config.tier3_collection_prefix}{user_id}"

    def _ensure_collection(self, collection_name: str) -> None:
        """Create collection if not exists.

        Args:
            collection_name: Name of the collection.
        """
        collections = [c.name for c in self.client.get_collections().collections]
        if collection_name not in collections:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=self.memory_config.colbert_vector_size,
                    distance=Distance.COSINE,
                    multivector_config=MultiVectorConfig(
                        comparator=MultiVectorComparator.MAX_SIM
                    ),
                ),
            )

    def _embed_text(self, text: str) -> list[list[float]]:
        """Embed text using ColBERT.

        Args:
            text: Input text.

        Returns:
            list[list[float]]: Multivector embeddings.
        """
        return list(self.embedder.embed([text]))[0]

    async def store_memory(
        self,
        content: str,
        user_id: str,
        memory_type: MemoryType = MemoryType.SEMANTIC,
        temporal_type: TemporalType = TemporalType.FACT,
        tier: int = 3,
        session_id: UUID | None = None,
        metadata: dict | None = None,
    ) -> UUID:
        """Store a memory with temporal metadata.

        Args:
            content: Memory content.
            user_id: User identifier.
            memory_type: Type of memory.
            temporal_type: Temporal classification.
            tier: Memory tier (2 or 3).
            session_id: Session ID for Tier 2.
            metadata: Additional metadata.

        Returns:
            UUID: The memory ID.
        """
        memory_id = uuid4()
        collection_name = self._get_collection_name(user_id, tier, session_id)
        self._ensure_collection(collection_name)

        # Embed content
        vectors = self._embed_text(content)

        # Build metadata
        now = datetime.now()
        memory_metadata = MemoryMetadata(
            user_id=user_id,
            session_id=str(session_id) if session_id else None,
            memory_type=memory_type,
            temporal_type=temporal_type,
            created_at=now,
            valid_from=now,
        )

        # Store in Qdrant
        point = PointStruct(
            id=str(memory_id),
            vector=vectors,
            payload={
                "content": content,
                **memory_metadata.model_dump(),
                **(metadata or {}),
            },
        )

        self.client.upsert(collection_name=collection_name, points=[point])

        return memory_id

    async def search_memories(
        self,
        query: str,
        user_id: str,
        tier: int = 3,
        session_id: UUID | None = None,
        limit: int = 10,
        time_filter: str = "all",
    ) -> list[dict]:
        """Search memories by query.

        Args:
            query: Search query.
            user_id: User identifier.
            tier: Memory tier to search.
            session_id: Session ID for Tier 2.
            limit: Maximum results.
            time_filter: Time filter (recent, historical, all).

        Returns:
            list[dict]: Search results with scores.
        """
        collection_name = self._get_collection_name(user_id, tier, session_id)

        # Check if collection exists
        collections = [c.name for c in self.client.get_collections().collections]
        if collection_name not in collections:
            return []

        # Embed query
        query_vectors = self._embed_text(query)

        # Build filter for time-based search
        # Note: Time filtering happens in TemporalRAGService application layer
        query_filter = None

        # Search
        results = self.client.search(
            collection_name=collection_name,
            query_vector=query_vectors,
            limit=limit,
            query_filter=query_filter,
        )

        return [
            {
                "memory_id": UUID(r.id),
                "content": r.payload.get("content", ""),
                "score": r.score,
                "metadata": {
                    k: v
                    for k, v in r.payload.items()
                    if k != "content" and not k.startswith("_")
                },
            }
            for r in results
        ]

    async def get_all_memories(
        self, user_id: str, tier: int = 2, session_id: UUID | None = None
    ) -> list[dict]:
        """Get all memories for a user/session.

        Args:
            user_id: User identifier.
            tier: Memory tier.
            session_id: Session ID for Tier 2.

        Returns:
            list[dict]: All memories.
        """
        collection_name = self._get_collection_name(user_id, tier, session_id)

        collections = [c.name for c in self.client.get_collections().collections]
        if collection_name not in collections:
            return []

        # Scroll through all points
        results = []
        offset = None
        while True:
            records, offset = self.client.scroll(
                collection_name=collection_name,
                limit=100,
                offset=offset,
            )
            results.extend(records)
            if offset is None:
                break

        return [
            {
                "memory_id": UUID(r.id),
                "content": r.payload.get("content", ""),
                "metadata": {
                    k: v
                    for k, v in r.payload.items()
                    if k != "content" and not k.startswith("_")
                },
            }
            for r in results
        ]
