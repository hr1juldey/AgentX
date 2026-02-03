"""Search memory use case.

Handles searching memories with temporal filtering and multi-hop retrieval.
From C005 memory-rag change.
"""

from __future__ import annotations

from uuid import UUID

from agentx.application.services.temporal_rag import TemporalRAGService
from agentx.domain.entities.enums import TemporalType
from agentx.infrastructure.database.qdrant_vector_store import QdrantVectorStore


class SearchMemoryUseCase:
    """Use case for searching memories with temporal filtering.

    Features:
    - Time-filtered search (recent, historical, all)
    - Multi-hop retrieval (Tier 2 + Tier 3)
    - Temporal type filtering
    - Fact invalidation
    """

    def __init__(
        self, vector_store: QdrantVectorStore, temporal_rag: TemporalRAGService
    ) -> None:
        """Initialize search memory use case.

        Args:
            vector_store: Qdrant vector store instance.
            temporal_rag: Temporal RAG service instance.
        """
        self._vector_store = vector_store
        self._temporal_rag = temporal_rag

    async def execute(
        self,
        query: str,
        user_id: str,
        time_filter: str = "all",
        tier: int = 3,
        session_id: UUID | None = None,
        max_results: int = 10,
        temporal_types: list[TemporalType] | None = None,
    ) -> dict:
        """Search memories with temporal filtering.

        Args:
            query: Search query.
            user_id: User identifier.
            time_filter: Time filter (recent, historical, all).
            tier: Memory tier to search.
            session_id: Session ID for Tier 2.
            max_results: Maximum results.
            temporal_types: Optional temporal type filter.

        Returns:
            dict: Search results with metadata.
        """
        import time

        start_time = time.time()

        # Perform temporal search
        results = await self._temporal_rag.search_with_temporal_filter(
            query=query,
            user_id=user_id,
            time_filter=time_filter,
            tier=tier,
            session_id=session_id,
            limit=max_results,
            temporal_types=temporal_types,
        )

        elapsed_ms = int((time.time() - start_time) * 1000)

        return {
            "results": [
                {
                    "memory_id": str(r.get("memory_id")),
                    "content": r.get("content"),
                    "temporal_type": r.get("metadata", {}).get("temporal_type"),
                    "created_at": r.get("metadata", {}).get("created_at"),
                    "valid_until": r.get("metadata", {}).get("valid_until"),
                    "score": r.get("weighted_score", r.get("score", 0)),
                    "superseded": r.get("superseded", False),
                }
                for r in results
            ],
            "total_found": len(results),
            "query_time_ms": elapsed_ms,
        }

    async def multi_hop_search(
        self,
        queries: list[str],
        user_id: str,
        tier: int = 3,
        limit_per_hop: int = 3,
    ) -> dict:
        """Multi-hop retrieval for complex queries.

        Args:
            queries: List of queries for each hop.
            user_id: User identifier.
            tier: Memory tier to search.
            limit_per_hop: Results per hop.

        Returns:
            dict: Multi-hop search results.
        """
        results = await self._temporal_rag.multi_hop_search(
            queries=queries,
            user_id=user_id,
            tier=tier,
            limit_per_hop=limit_per_hop,
        )

        return {
            "results": [
                {
                    "memory_id": str(r.get("memory_id")),
                    "content": r.get("content"),
                    "score": r.get("score", 0),
                    "metadata": r.get("metadata", {}),
                }
                for r in results
            ],
            "total_found": len(results),
            "hops": len(queries),
        }
