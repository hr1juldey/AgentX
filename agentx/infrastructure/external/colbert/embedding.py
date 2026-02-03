"""ColBERT embedding operations.

Handles text and query embedding using ColBERTv2.
"""

from fastembed import LateInteractionTextEmbedding

from agentx.core.memory_config import get_memory_config


class ColBERTEmbedding:
    """ColBERTv2 embedding operations.

    Phase 4 Fix: Uses memory_config for model name and vector size (Fraud #3.3).
    """

    def __init__(self) -> None:
        """Initialize embedding model (lazy-loaded)."""
        self._embedder: LateInteractionTextEmbedding | None = None

    @property
    def model_name(self) -> str:
        """Get ColBERT model name from config."""
        return get_memory_config().colbert_model_name

    @property
    def vector_size(self) -> int:
        """Get ColBERT vector size from config."""
        return get_memory_config().colbert_vector_size

    @property
    def embedder(self) -> LateInteractionTextEmbedding:
        """Lazy-load ColBERT model (expensive, ~440MB)."""
        if self._embedder is None:
            self._embedder = LateInteractionTextEmbedding(
                model_name=self.model_name,
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
