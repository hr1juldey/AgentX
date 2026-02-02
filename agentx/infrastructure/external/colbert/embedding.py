"""ColBERT embedding operations.

Handles text and query embedding using ColBERTv2.
"""

from fastembed import LateInteractionTextEmbedding


class ColBERTEmbedding:
    """ColBERTv2 embedding operations."""

    MODEL_NAME = "colbert-ir/colbertv2.0"
    VECTOR_SIZE = 128

    def __init__(self) -> None:
        """Initialize embedding model (lazy-loaded)."""
        self._embedder: LateInteractionTextEmbedding | None = None

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
