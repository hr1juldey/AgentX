"""Embedding service for Qdrant vector store.

Handles ColBERT text embedding for multivector storage.
"""

from fastembed import LateInteractionTextEmbedding


class ColBERTEmbedder:
    """Lazy-loaded ColBERT embedder.

    Delays model loading until first use to reduce startup time.
    """

    def __init__(self, model_name: str):
        """Initialize embedder without loading the model.

        Args:
            model_name: Name of the ColBERT model to use.
        """
        self.model_name = model_name
        self._embedder: LateInteractionTextEmbedding | None = None

    @property
    def embedder(self) -> LateInteractionTextEmbedding:
        """Lazy-load ColBERT embedder.

        Returns:
            LateInteractionTextEmbedding: ColBERT embedder instance.
        """
        if self._embedder is None:
            self._embedder = LateInteractionTextEmbedding(self.model_name)
        return self._embedder

    def embed_text(self, text: str) -> list[list[float]]:
        """Embed text using ColBERT.

        Args:
            text: Input text.

        Returns:
            list[list[float]]: Multivector embeddings.
        """
        return list(self.embedder.embed([text]))[0]  # type: ignore[return-value]
