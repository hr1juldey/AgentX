"""Qdrant vector store for Real AgentX v0.1.

Composes all Qdrant services into a single interface.
"""

from uuid import UUID

from qdrant_client import QdrantClient

from agentx.core.config import get_settings
from agentx.core.memory_config import get_memory_config
from agentx.domain.entities.enums import MemoryType, TemporalType
from agentx.infrastructure.database.qdrant.embedding_service import ColBERTEmbedder
from agentx.infrastructure.database.qdrant.models import MemoryMetadata
from agentx.infrastructure.database.qdrant.retrieve import (
    get_all_memories as _get_all_memories,
)
from agentx.infrastructure.database.qdrant.search_operations import (
    search_memories as _search_memories,
)
from agentx.infrastructure.database.qdrant.store import store_memory as _store_memory


class QdrantVectorStore:
    """Qdrant adapter for ColBERT multivector storage.

    Supports Tier 2 (session-scoped) and Tier 3 (persistent) memories.
    """

    def __init__(self) -> None:
        settings = get_settings()
        self.client = QdrantClient(url=settings.database.qdrant_url)
        self.memory_config = get_memory_config()
        self._embedder: ColBERTEmbedder | None = None

    @property
    def embedder(self) -> ColBERTEmbedder:
        if self._embedder is None:
            self._embedder = ColBERTEmbedder(self.memory_config.colbert_model_name)
        return self._embedder

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
        return await _store_memory(
            self.client,
            self.embedder,
            content,
            user_id,
            memory_type,
            temporal_type,
            tier,
            session_id,
            metadata,
            self.memory_config,
        )

    async def search_memories(
        self,
        query: str,
        user_id: str,
        tier: int = 3,
        session_id: UUID | None = None,
        limit: int = 10,
        time_filter: str = "all",
    ) -> list[dict]:
        return await _search_memories(
            self.client,
            self.embedder,
            query,
            user_id,
            tier,
            session_id,
            limit,
            time_filter,
            self.memory_config,
        )

    async def get_all_memories(
        self, user_id: str, tier: int = 2, session_id: UUID | None = None
    ) -> list[dict]:
        return await _get_all_memories(
            self.client,
            user_id,
            tier,
            session_id,
            self.memory_config,
        )


__all__ = ["MemoryMetadata", "QdrantVectorStore"]
