"""Temporal RAG service for Real AgentX v0.1.

Composes all temporal RAG functionality into a single interface.
"""

from typing import Any
from uuid import UUID

from agentx.domain.entities.enums import TemporalType
from agentx.infrastructure.database.qdrant_vector_store import QdrantVectorStore
from agentx.application.services.temporal_rag.result_processor import (
    invalidate_outdated_facts,
    weight_results,
)
from agentx.application.services.temporal_rag.search_strategies import (
    multi_hop_search as _multi_hop_search,
    search_with_temporal_filter as _search_with_temporal_filter,
)
from agentx.application.services.temporal_rag.temporal_classifier import (
    classify_temporal_type,
)
from agentx.application.services.temporal_rag.temporal_metadata import (
    add_temporal_metadata,
)


class TemporalRAGService:
    """Service for time-aware RAG operations.

    Features:
    - Temporal metadata enrichment
    - Temporal classification
    - Time-filtered search
    - Fact invalidation
    - Multi-hop retrieval
    """

    def __init__(self, vector_store: QdrantVectorStore) -> None:
        """Initialize temporal RAG service.

        Args:
            vector_store: Qdrant vector store instance.
        """
        self._vector_store = vector_store

    def add_temporal_metadata(
        self, content: str, temporal_type: TemporalType | None = None
    ) -> dict[str, Any]:
        """Add temporal metadata to memory."""
        return add_temporal_metadata(content, temporal_type)

    def _classify_temporal_type(self, content: str) -> TemporalType:
        """Classify memory by temporal type."""
        return classify_temporal_type(content)

    async def search_with_temporal_filter(
        self,
        query: str,
        user_id: str,
        time_filter: str = "all",
        tier: int = 3,
        session_id: UUID | None = None,
        limit: int = 10,
        temporal_types: list[TemporalType] | None = None,
    ) -> list[dict]:
        """Search memories with temporal filtering."""
        return await _search_with_temporal_filter(
            self._vector_store,
            query,
            user_id,
            time_filter,
            tier,
            session_id,
            limit,
            temporal_types,
        )

    def _invalidate_outdated_facts(self, results: list[dict]) -> list[dict]:
        """Mark outdated facts in results."""
        return invalidate_outdated_facts(results)

    def _weight_results(self, results: list[dict]) -> list[dict]:
        """Weight results by temporal type."""
        return weight_results(results)

    async def multi_hop_search(
        self,
        queries: list[str],
        user_id: str,
        tier: int = 3,
        limit_per_hop: int = 3,
    ) -> list[dict]:
        """Multi-hop retrieval for complex queries."""
        return await _multi_hop_search(
            self._vector_store,
            queries,
            user_id,
            tier,
            limit_per_hop,
        )
