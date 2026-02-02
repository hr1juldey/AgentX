"""Store operation for Qdrant vector store.

Handles memory storage with temporal metadata.
"""

from datetime import datetime
from uuid import UUID, uuid4

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

from agentx.core.memory_config import get_memory_config
from agentx.domain.entities.enums import MemoryType, TemporalType
from agentx.infrastructure.database.qdrant.collection_service import (
    ensure_collection,
    get_collection_name,
)
from agentx.infrastructure.database.qdrant.models import MemoryMetadata


async def store_memory(
    client: QdrantClient,
    embedder: object,
    content: str,
    user_id: str,
    memory_type: MemoryType = MemoryType.SEMANTIC,
    temporal_type: TemporalType = TemporalType.FACT,
    tier: int = 3,
    session_id: UUID | None = None,
    metadata: dict | None = None,
    memory_config: object = None,
) -> UUID:
    """Store a memory with temporal metadata.

    Args:
        client: Qdrant client instance.
        embedder: ColBERT embedder instance.
        content: Memory content.
        user_id: User identifier.
        memory_type: Type of memory.
        temporal_type: Temporal classification.
        tier: Memory tier (2 or 3).
        session_id: Session ID for Tier 2.
        metadata: Additional metadata.
        memory_config: Memory configuration object.

    Returns:
        UUID: The memory ID.
    """
    if memory_config is None:
        memory_config = get_memory_config()

    memory_id = uuid4()
    collection_name = get_collection_name(user_id, tier, session_id, memory_config)
    ensure_collection(client, collection_name, memory_config)

    # Embed content
    vectors = embedder.embed_text(content)  # type: ignore[attr-defined]

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

    client.upsert(collection_name=collection_name, points=[point])

    return memory_id
