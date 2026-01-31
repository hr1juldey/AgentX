"""Temporal RAG service for time-aware memory retrieval.

Implements temporal filtering, fact invalidation, and multi-hop search.
From C005 memory-rag change.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from agentx.core.memory_config import get_memory_config
from agentx.domain.entities.enums import TemporalType
from agentx.infrastructure.database.qdrant_vector_store import QdrantVectorStore


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
        self._memory_config = get_memory_config()

    def add_temporal_metadata(
        self, content: str, temporal_type: TemporalType | None = None
    ) -> dict[str, Any]:
        """Add temporal metadata to memory.

        Args:
            content: Memory content.
            temporal_type: Optional pre-classified type.

        Returns:
            dict: Temporal metadata.
        """
        now = datetime.now()

        if temporal_type is None:
            temporal_type = self._classify_temporal_type(content)

        return {
            "created_at": now,
            "modified_at": now,
            "valid_from": now,
            "valid_until": None,
            "temporal_type": temporal_type,
            "supersedes": [],
            "superseded_by": None,
        }

    def _classify_temporal_type(self, content: str) -> TemporalType:
        """Classify memory by temporal type.

        Args:
            content: Memory content.

        Returns:
            TemporalType: Classified type.
        """
        content_lower = content.lower()

        # Preference patterns
        if any(
            word in content_lower
            for word in ["prefer", "like", "want", "choose", "favorite"]
        ):
            return TemporalType.PREFERENCE

        # State patterns
        if any(
            word in content_lower
            for word in ["status", "state", "condition", "current", "progress"]
        ):
            return TemporalType.STATE

        # Event patterns
        if any(
            word in content_lower
            for word in ["happened", "occurred", "meeting", "call", "discussed"]
        ):
            return TemporalType.EVENT

        # Plan patterns
        if any(
            word in content_lower
            for word in ["will", "plan", "schedule", "upcoming", "future", "tomorrow"]
        ):
            return TemporalType.PLAN

        # Default to fact
        return TemporalType.FACT

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
        """Search memories with temporal filtering.

        Args:
            query: Search query.
            user_id: User identifier.
            time_filter: Time filter (recent, historical, all).
            tier: Memory tier to search.
            session_id: Session ID for Tier 2.
            limit: Maximum results.
            temporal_types: Optional temporal type filter.

        Returns:
            list[dict]: Filtered search results.
        """
        # Get raw results
        results = await self._vector_store.search_memories(
            query=query,
            user_id=user_id,
            tier=tier,
            session_id=session_id,
            limit=limit * 2,  # Get more for filtering
            time_filter=time_filter,
        )

        # Apply time-based filtering
        if time_filter == "recent":
            cutoff = datetime.now() - timedelta(
                days=self._memory_config.recent_days_threshold
            )
            results = [
                r
                for r in results
                if r["metadata"].get("created_at", datetime.min) >= cutoff.isoformat()
            ]
        elif time_filter == "historical":
            cutoff = datetime.now() - timedelta(
                days=self._memory_config.recent_days_threshold
            )
            results = [
                r
                for r in results
                if r["metadata"].get("created_at", datetime.min) < cutoff.isoformat()
            ]

        # Apply temporal type filtering
        if temporal_types:
            results = [
                r
                for r in results
                if r["metadata"].get("temporal_type")
                in [t.value for t in temporal_types]
            ]

        # Invalidate outdated facts
        results = self._invalidate_outdated_facts(results)

        # Weight results (preferences > facts > events > states > plans)
        results = self._weight_results(results)

        return results[:limit]

    def _invalidate_outdated_facts(self, results: list[dict]) -> list[dict]:
        """Mark outdated facts in results.

        Args:
            results: Search results.

        Returns:
            list[dict]: Results with outdated facts marked.
        """
        for result in results:
            metadata = result.get("metadata", {})
            if metadata.get("superseded_by"):
                result["superseded"] = True
            else:
                result["superseded"] = False

        return results

    def _weight_results(self, results: list[dict]) -> list[dict]:
        """Weight results by temporal type.

        Args:
            results: Search results.

        Returns:
            list[dict]: Weighted and sorted results.
        """
        # Temporal type weights
        weights = {
            TemporalType.PREFERENCE: 1.5,
            TemporalType.FACT: 1.2,
            TemporalType.EVENT: 1.0,
            TemporalType.STATE: 0.8,
            TemporalType.PLAN: 0.6,
        }

        for result in results:
            temporal_type = result["metadata"].get("temporal_type", TemporalType.FACT)
            base_score = result.get("score", 0.5)
            weight = weights.get(temporal_type, 1.0)
            result["weighted_score"] = base_score * weight

        # Sort by weighted score
        results.sort(key=lambda r: r.get("weighted_score", 0), reverse=True)

        return results

    async def multi_hop_search(
        self,
        queries: list[str],
        user_id: str,
        tier: int = 3,
        limit_per_hop: int = 3,
    ) -> list[dict]:
        """Multi-hop retrieval for complex queries.

        Args:
            queries: List of queries for each hop.
            user_id: User identifier.
            tier: Memory tier to search.
            limit_per_hop: Results per hop.

        Returns:
            list[dict]: Consolidated multi-hop results.
        """
        all_results = {}
        seen_ids = set()

        for query in queries:
            results = await self._vector_store.search_memories(
                query=query,
                user_id=user_id,
                tier=tier,
                limit=limit_per_hop,
            )

            for result in results:
                memory_id = str(result.get("memory_id"))
                if memory_id not in seen_ids:
                    seen_ids.add(memory_id)
                    all_results[memory_id] = result

        return list(all_results.values())
