"""Time-filtered search for temporal RAG.

Handles temporal filtering of search results.
"""

from datetime import datetime, timedelta
from uuid import UUID

from agentx.core.memory_config import get_memory_config
from agentx.domain.entities.enums import TemporalType
from agentx.infrastructure.database.qdrant_vector_store import QdrantVectorStore
from agentx.application.services.temporal_rag.result_processor import (
    invalidate_outdated_facts,
    weight_results,
)


async def search_with_temporal_filter(
    vector_store: QdrantVectorStore,
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
        vector_store: Qdrant vector store instance.
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
    memory_config = get_memory_config()

    # Get raw results
    results = await vector_store.search_memories(
        query=query,
        user_id=user_id,
        tier=tier,
        session_id=session_id,
        limit=limit * 2,  # Get more for filtering
        time_filter=time_filter,
    )

    # Apply time-based filtering
    if time_filter == "recent":
        cutoff = datetime.now() - timedelta(days=memory_config.recent_days_threshold)
        results = [
            r
            for r in results
            if r["metadata"].get("created_at", datetime.min) >= cutoff.isoformat()
        ]
    elif time_filter == "historical":
        cutoff = datetime.now() - timedelta(days=memory_config.recent_days_threshold)
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
            if r["metadata"].get("temporal_type") in [t.value for t in temporal_types]
        ]

    # Invalidate outdated facts
    results = invalidate_outdated_facts(results)

    # Weight results (preferences > facts > events > states > plans)
    results = weight_results(results)

    return results[:limit]
