"""Sentence-transformers embedding backend."""

import logging


logger = logging.getLogger(__name__)


class SentenceTransformerEmbedder:
    """Sentence-transformers embedding backend for dense vectorization."""

    def __init__(self, model_name: str) -> None:
        """Initialize sentence-transformers embedder.

        Args:
            model_name: Model name (e.g., "all-MiniLM-L6-v2")
        """
        from sentence_transformers import SentenceTransformer

        self._model = SentenceTransformer(model_name)
        self.model_name = model_name
        logger.info(f"SentenceTransformerEmbedder initialized: {model_name}")

    def embed(self, text: str) -> list[float]:
        """Generate embedding for text.

        Args:
            text: Input text to embed

        Returns:
            Embedding vector
        """
        embedding = self._model.encode(text)  # type: ignore[assignment]
        if isinstance(embedding, list):
            result = embedding
        else:
            result = embedding.tolist()
        logger.debug(
            f"sentence-transformers embedding: dim={len(result)}, text='{text[:30]}...'"
        )
        return result

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple texts efficiently.

        Args:
            texts: List of input texts

        Returns:
            List of embedding vectors
        """
        try:
            embeddings = self._model.encode(texts)  # type: ignore[assignment]
            if isinstance(embeddings, list):
                return embeddings
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Batch embedding failed: {e}")
            # Fallback to individual embedding
            return [self.embed(text) for text in texts]
