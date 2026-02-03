"""ColBERT embedder for semantic search.

Composes embedding, Qdrant management, and search/store operations.
"""

from agentx.infrastructure.external.colbert.embedding import ColBERTEmbedding
from agentx.infrastructure.external.colbert.qdrant_manager import (
    ColBERTQdrantManager,
)
from agentx.infrastructure.external.colbert.search_operations import (
    ColBERTSearchOperations,
)
from agentx.infrastructure.external.colbert.store_operations import (
    ColBERTStoreOperations,
)


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

    def __init__(self, qdrant_url: str = "http://localhost:6335") -> None:
        """Initialize ColBERT embedder.

        Args:
            qdrant_url: Qdrant server URL
        """
        self._embedding = ColBERTEmbedding()
        self._qdrant = ColBERTQdrantManager(qdrant_url)
        self.client = self._qdrant.client

        # Initialize operations
        self._search = ColBERTSearchOperations(self.client, self._embedding.query_embed)
        self._store = ColBERTStoreOperations(
            self.client, self._embedding.embed_text, self._qdrant.ensure_collection
        )

    @property
    def embedder(self):
        """Access to embedding model."""
        return self._embedding.embedder

    def embed_text(self, text: str) -> list[list[float]]:
        """Embed text as multivectors (one vector per token)."""
        return self._embedding.embed_text(text)

    def query_embed(self, query: str) -> list[list[float]]:
        """Embed query for search (optimized for retrieval)."""
        return self._embedding.query_embed(query)

    def ensure_collection(self, collection_name: str) -> None:
        """Create Qdrant collection with multivector config."""
        return self._qdrant.ensure_collection(collection_name)

    async def search(
        self,
        collection_name: str,
        query: str,
        limit: int = 10,
        user_id: str | None = None,
    ) -> list[dict]:
        """Semantic search using ColBERT late interaction."""
        return await self._search.search(collection_name, query, limit, user_id)

    async def store(
        self,
        collection_name: str,
        content: str,
        memory_id: str,
        user_id: str,
        metadata: dict,
    ) -> None:
        """Store content with ColBERT embeddings."""
        return await self._store.store(
            collection_name, content, memory_id, user_id, metadata
        )
