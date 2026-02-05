"""Dense vectorizer for single-vector embeddings.

Uses sentence transformer models to convert text to dense vectors.

Defaults to using Ollama's embedding API for fully local operation.

Note: All embeddings are resized to 1024 dimensions to match
QdrantCollectionManager's DENSE_DIM configuration.
"""

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

from agentx.infrastructure.retrieval.vectorizer.ollama import (
    OllamaEmbedder,
)
from agentx.infrastructure.retrieval.vectorizer.sentence_transformers import (
    SentenceTransformerEmbedder,
)

logger = logging.getLogger(__name__)


class DenseVectorizer:
    """Dense vectorizer using sentence transformer models.

    Provides single-vector embeddings for text using models like
    all-MiniLM-L6-v2 or Ollama embeddings.

    Defaults to using Ollama's embedding API for fully local operation.

    Note: All embeddings are resized to 1024 dimensions to match
    QdrantCollectionManager's DENSE_DIM configuration.
    """

    # Target dimension for Qdrant compatibility
    TARGET_DIM = 1024

    def __init__(self, model_name: str = "mxbai-embed-large:latest") -> None:
        """Initialize the dense vectorizer.

        Args:
            model_name: Model name for embeddings.
                - For Ollama: use "mxbai-embed-large:latest", "nomic-embed-text", etc.
                - For sentence-transformers: use "all-MiniLM-L6-v2", etc.
        """
        self.model_name = model_name
        self._use_ollama = ":" in model_name  # Detect Ollama model format

        if self._use_ollama:
            try:
                self._ollama_embedder = OllamaEmbedder(model_name)
                logger.info(f"DenseVectorizer using Ollama: {model_name}")
            except ImportError:
                logger.warning(
                    "Ollama client not available, falling back to sentence-transformers"
                )
                self._use_ollama = False
            except Exception as e:
                logger.warning(
                    f"Ollama connection failed: {e}, falling back to sentence-transformers"
                )
                self._use_ollama = False

        if not self._use_ollama:
            try:
                self._st_embedder = SentenceTransformerEmbedder(model_name)
                logger.info(
                    f"DenseVectorizer using sentence-transformers: {model_name}"
                )
            except ImportError:
                raise ImportError(
                    "Neither ollama nor sentence-transformers is available. "
                    "Install one with: pip install ollama  or  pip install sentence-transformers"
                )

    def embed(self, text: str) -> list[float]:
        """Convert text to dense vector embedding.

        Args:
            text: Input text to embed

        Returns:
            List of float values representing the embedding vector
        """
        if self._use_ollama:
            return self._ollama_embedder.embed(text)
        return self._st_embedder.embed(text)

    @property
    def dimension(self) -> int:
        """Get the embedding dimension.

        Returns:
            Size of the embedding vector (always TARGET_DIM after resizing)
        """
        return self.TARGET_DIM

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple texts efficiently.

        Args:
            texts: List of input texts to embed

        Returns:
            List of embedding vectors
        """
        if self._use_ollama:
            return self._ollama_embedder.embed_batch(texts)
        return self._st_embedder.embed_batch(texts)
