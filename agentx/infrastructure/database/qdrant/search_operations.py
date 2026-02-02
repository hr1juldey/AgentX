"""Search operations for Qdrant vector store.

Handles semantic search with multivector embeddings.
"""

from uuid import UUID

from qdrant_client import QdrantClient

from agentx.core.memory_config import get_memory_config
from agentx.infrastructure.database.qdrant.collection_service import get_collection_name


async def search_memories(
    client: QdrantClient,
    embedder: object,
    query: str,
    user_id: str,
    tier: int = 3,
    session_id: UUID | None = None,
    limit: int = 10,
    time_filter: str = "all",
    memory_config: object = None,
) -> list[dict]:
    """Search memories by query.

    Args:
        client: Qdrant client instance.
        embedder: ColBERT embedder instance.
        query: Search query.
        user_id: User identifier.
        tier: Memory tier to search.
        session_id: Session ID for Tier 2.
        limit: Maximum results.
        time_filter: Time filter (recent, historical, all).
        memory_config: Memory configuration object.

    Returns:
        list[dict]: Search results with scores.
    """
    if memory_config is None:
        memory_config = get_memory_config()

    collection_name = get_collection_name(user_id, tier, session_id, memory_config)

    # Check if collection exists
    collections = [c.name for c in client.get_collections().collections]
    if collection_name not in collections:
        return []

    # Embed query
    query_vectors = embedder.embed_text(query)  # type: ignore[attr-defined]

    # Build filter for time-based search
    # Note: Time filtering happens in TemporalRAGService application layer
    query_filter = None

    # Search
    results = client.search(  # type: ignore[attr-defined]
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
