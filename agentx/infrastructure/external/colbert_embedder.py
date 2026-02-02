"""ColBERT embedder for semantic search.

This module provides ColBERTv2 late interaction embedder for Qdrant.
ColBERT provides token-level granularity with MaxSim operation.
"""

from typing import TYPE_CHECKING

from fastembed import LateInteractionTextEmbedding
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    Filter,
    FieldCondition,
    MultiVectorConfig,
    MultiVectorComparator,
    PointStruct,
    VectorParams,
)

if TYPE_CHECKING:
    pass


class ColBERTEmbedder:
    """ColBERTv2 late interaction embedder for semantic search.

    Why ColBERT?
    - Token-level granularity (preserves fine-grained semantics)
    - Late interaction (efficient MaxSim operation)
    - Multivector output (each token → 128-dim vector)
    - State-of-the-art retrieval performance
    """

    MODEL_NAME = "colbert-ir/colbertv2.0"
    VECTOR_SIZE = 128

    def __init__(self, qdrant_url: str = "http://localhost:6333"):
        """Initialize ColBERT embedder.

        Args:
            qdrant_url: Qdrant server URL
        """
        self._embedder: LateInteractionTextEmbedding | None = None
        self.client = QdrantClient(url=qdrant_url)

    @property
    def embedder(self) -> LateInteractionTextEmbedding:
        """Lazy-load ColBERT model (expensive, ~440MB)."""
        if self._embedder is None:
            self._embedder = LateInteractionTextEmbedding(
                model_name=self.MODEL_NAME,
            )
        return self._embedder

    def embed_text(self, text: str) -> list[list[float]]:
        """Embed text as multivectors (one vector per token).

        Args:
            text: Text to embed

        Returns:
            list[list[float]]: Multivector embedding (num_tokens × 128)
        """
        embeddings = list(self.embedder.embed([text]))
        return list(list(map(float, v)) for v in embeddings[0])  # type: ignore[return-value]

    def query_embed(self, query: str) -> list[list[float]]:
        """Embed query for search (optimized for retrieval).

        Args:
            query: Search query

        Returns:
            list[list[float]]: Query multivectors
        """
        embeddings = list(self.embedder.query_embed([query]))
        return list(list(map(float, v)) for v in embeddings[0])  # type: ignore[return-value]

    def ensure_collection(self, collection_name: str) -> None:
        """Create Qdrant collection with multivector config.

        Args:
            collection_name: Name of the collection
        """
        collections = [c.name for c in self.client.get_collections().collections]
        if collection_name not in collections:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=self.VECTOR_SIZE,
                    distance=Distance.COSINE,
                    multivector_config=MultiVectorConfig(
                        comparator=MultiVectorComparator.MAX_SIM
                    ),
                ),
            )

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
        query_vectors = self.query_embed(query)

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
        self.ensure_collection(collection_name)

        vectors = self.embed_text(content)

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
