"""ColBERT store operations.

Handles storing content with embeddings in Qdrant.
"""

from collections.abc import Callable
from typing import TYPE_CHECKING

from qdrant_client.models import PointStruct

if TYPE_CHECKING:
    from qdrant_client import QdrantClient


class ColBERTStoreOperations:
    """Store operations for ColBERT embeddings."""

    def __init__(
        self,
        qdrant_client: "QdrantClient",
        embed_fn: Callable[[str], list[list[float]]],
        ensure_collection_fn: Callable[[str], None],
    ) -> None:
        """Initialize store operations.

        Args:
            qdrant_client: Qdrant client instance
            embed_fn: Text embedding function
            ensure_collection_fn: Function to ensure collection exists
        """
        self.client = qdrant_client
        self._embed_fn = embed_fn
        self._ensure_collection = ensure_collection_fn

    async def store(
        self,
        collection_name: str,
        content: str,
        memory_id: str,
        user_id: str,
        metadata: dict,
    ) -> None:
        """Store content with ColBERT embeddings.

        Args:
            collection_name: Qdrant collection name
            content: Content to store
            memory_id: Unique ID
            user_id: User ID for isolation
            metadata: Additional metadata
        """
        self._ensure_collection(collection_name)

        vectors = self._embed_fn(content)

        self.client.upsert(
            collection_name=collection_name,
            points=[
                PointStruct(
                    id=memory_id,
                    vector=vectors,
                    payload={
                        "content": content,
                        "user_id": user_id,
                        **metadata,
                    },
                )
            ],
        )
