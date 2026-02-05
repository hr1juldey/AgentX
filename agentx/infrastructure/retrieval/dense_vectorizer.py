"""Dense vectorizer for single-vector embeddings.

Uses sentence transformer models to convert text to dense vectors.
"""

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

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
                from ollama import Client

                self._ollama_client = Client(host="http://localhost:11434")
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
                from sentence_transformers import SentenceTransformer

                self._model = SentenceTransformer(model_name)
                logger.info(
                    f"DenseVectorizer using sentence-transformers: {model_name}"
                )
            except ImportError:
                raise ImportError(
                    "Neither ollama nor sentence-transformers is available. "
                    "Install one with: pip install ollama  or  pip install sentence-transformers"
                )

    def embed(self, text: str) -> "list[float]":
        """Convert text to dense vector embedding.

        Args:
            text: Input text to embed

        Returns:
            List of float values representing the embedding vector
        """
        if self._use_ollama:
            return self._embed_ollama(text)
        return self._embed_sentence_transformers(text)

    def _embed_ollama(self, text: str) -> "list[float]":
        """Embed using Ollama API.

        Args:
            text: Input text to embed

        Returns:
            List of float values representing the embedding vector
            (resized to TARGET_DIM for Qdrant compatibility)
        """
        try:
            response = self._ollama_client.embeddings(
                model=self.model_name, prompt=text
            )
            embedding = response.get("embedding", [])

            # Resize to TARGET_DIM for Qdrant compatibility
            # (e.g., qwen3-embedding:8b produces 4096D, we need 1024D)
            original_dim = len(embedding)
            if original_dim > self.TARGET_DIM:
                embedding = embedding[: self.TARGET_DIM]
                logger.debug(
                    f"Ollama embedding resized: {original_dim}D -> {len(embedding)}D, "
                    f"model={self.model_name}, text='{text[:30]}...'"
                )
            else:
                logger.debug(
                    f"Ollama embedding: dim={len(embedding)}, text='{text[:30]}...'"
                )
            return embedding
        except Exception as e:
            logger.error(f"Ollama embedding failed: {e}")
            raise

    def _embed_sentence_transformers(self, text: str) -> "list[float]":
        """Embed using sentence-transformers.

        Args:
            text: Input text to embed

        Returns:
            List of float values representing the embedding vector
        """
        try:
            embedding = self._model.encode(text)  # type: ignore[assignment]
            if isinstance(embedding, list):
                result = embedding
            else:
                result = embedding.tolist()
            logger.debug(
                f"sentence-transformers embedding: dim={len(result)}, text='{text[:30]}...'"
            )
            return result
        except Exception as e:
            logger.error(f"sentence-transformers embedding failed: {e}")
            raise

    @property
    def dimension(self) -> int:
        """Get the embedding dimension.

        Returns:
            Size of the embedding vector (always TARGET_DIM after resizing)
        """
        return self.TARGET_DIM

    def embed_batch(self, texts: list[str]) -> "list[list[float]]":
        """Embed multiple texts efficiently.

        Args:
            texts: List of input texts to embed

        Returns:
            List of embedding vectors
        """
        if self._use_ollama:
            # Ollama doesn't have batch API, embed individually
            return [self.embed(text) for text in texts]
        else:
            # sentence-transformers has efficient batch processing
            try:
                embeddings = self._model.encode(texts)  # type: ignore[assignment]
                if isinstance(embeddings, list):
                    return embeddings
                return embeddings.tolist()
            except Exception as e:
                logger.error(f"Batch embedding failed: {e}")
                # Fallback to individual embedding
                return [self.embed(text) for text in texts]
