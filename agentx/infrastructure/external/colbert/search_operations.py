"""ColBERT search operations.

Performs semantic search using Qdrant.
"""

from collections.abc import Callable
from typing import TYPE_CHECKING

from qdrant_client.models import FieldCondition, Filter

if TYPE_CHECKING:
    from qdrant_client import QdrantClient


class ColBERTSearchOperations:
    """Search operations for ColBERT embeddings."""

    def __init__(
        self,
        qdrant_client: "QdrantClient",
        embed_fn: Callable[[str], list[list[float]]],
    ) -> None:
        """Initialize search operations.

        Args:
            qdrant_client: Qdrant client instance
            embed_fn: Query embedding function
        """
        self.client = qdrant_client
        self._embed_fn = embed_fn

    async def search(
        self,
        collection_name: str,
        query: str,
        limit: int = 10,
        user_id: str | None = None,
    ) -> list[dict]:
        """Semantic search using ColBERT late interaction.

        Args:
            collection_name: Qdrant collection name
            query: Search query
            limit: Max results
            user_id: Optional filter

        Returns:
            list[dict]: Search results with scores
        """
        query_vectors = self._embed_fn(query)

        # Build filter (user isolation)
        query_filter = None
        if user_id:
            query_filter = Filter(
                must=[FieldCondition(key="user_id", match={"value": user_id})]
            )

        results = self.client.search(  # type: ignore[attr-defined]
            collection_name=collection_name,
            query_vector=query_vectors,
            limit=limit,
            query_filter=query_filter,
        )

        return [
            {
                "content": r.payload.get("content", ""),
                "score": r.score,
                "metadata": {
                    k: v for k, v in r.payload.items() if k not in ["content", "_id"]
                },
            }
            for r in results
        ]
