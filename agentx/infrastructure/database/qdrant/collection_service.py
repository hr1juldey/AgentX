"""Collection management for Qdrant vector store.

Handles collection creation, naming, and configuration.
"""

from uuid import UUID

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    MultiVectorComparator,
    MultiVectorConfig,
    VectorParams,
)

from agentx.core.memory_config import get_memory_config


def get_collection_name(
    user_id: str,
    tier: int = 3,
    session_id: UUID | None = None,
    memory_config: object = None,
) -> str:
    """Get collection name for tier and user.

    Args:
        user_id: User identifier.
        tier: Memory tier (2 or 3).
        session_id: Session ID for Tier 2.
        memory_config: Memory configuration object.

    Returns:
        str: Collection name.
    """
    if memory_config is None:
        memory_config = get_memory_config()

    if tier == 2 and session_id:
        return f"{memory_config.tier2_collection_prefix}{user_id}_session_{session_id}"  # type: ignore[attr-defined]
    return f"{memory_config.tier3_collection_prefix}{user_id}"  # type: ignore[attr-defined]


def ensure_collection(
    client: QdrantClient,
    collection_name: str,
    memory_config: object = None,
) -> None:
    """Create collection if not exists.

    Args:
        client: Qdrant client instance.
        collection_name: Name of the collection.
        memory_config: Memory configuration object.
    """
    if memory_config is None:
        memory_config = get_memory_config()

    collections = [c.name for c in client.get_collections().collections]
    if collection_name not in collections:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=memory_config.colbert_vector_size,  # type: ignore[attr-defined]
                distance=Distance.COSINE,
                multivector_config=MultiVectorConfig(
                    comparator=MultiVectorComparator.MAX_SIM
                ),
            ),
        )
