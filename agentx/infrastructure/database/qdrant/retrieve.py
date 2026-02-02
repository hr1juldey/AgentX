"""Retrieve operations for Qdrant vector store.

Handles retrieval of all memories for a user/session.
"""

from uuid import UUID

from qdrant_client import QdrantClient

from agentx.core.memory_config import get_memory_config
from agentx.infrastructure.database.qdrant.collection_service import get_collection_name


async def get_all_memories(
    client: QdrantClient,
    user_id: str,
    tier: int = 2,
    session_id: UUID | None = None,
    memory_config: object = None,
) -> list[dict]:
    """Get all memories for a user/session.

    Args:
        client: Qdrant client instance.
        user_id: User identifier.
        tier: Memory tier.
        session_id: Session ID for Tier 2.
        memory_config: Memory configuration object.

    Returns:
        list[dict]: All memories.
    """
    if memory_config is None:
        memory_config = get_memory_config()

    collection_name = get_collection_name(user_id, tier, session_id, memory_config)

    collections = [c.name for c in client.get_collections().collections]
    if collection_name not in collections:
        return []

    # Scroll through all points
    results = []
    offset = None
    while True:
        records, offset = client.scroll(
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
