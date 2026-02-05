"""Ollama-based embedding backend."""

import logging


logger = logging.getLogger(__name__)


class OllamaEmbedder:
    """Ollama embedding backend for dense vectorization."""

    TARGET_DIM = 1024

    def __init__(self, model_name: str) -> None:
        """Initialize Ollama embedder.

        Args:
            model_name: Ollama model name (e.g., "mxbai-embed-large:latest")
        """
        from ollama import Client

        self.model_name = model_name
        self._client = Client(host="http://localhost:11434")
        logger.info(f"OllamaEmbedder initialized: {model_name}")

    def embed(self, text: str) -> list[float]:
        """Generate embedding for text.

        Args:
            text: Input text to embed

        Returns:
            Embedding vector (resized to TARGET_DIM for Qdrant compatibility)
        """
        response = self._client.embeddings(model=self.model_name, prompt=text)
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

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple texts (no batch API, processes individually).

        Args:
            texts: List of input texts

        Returns:
            List of embedding vectors
        """
        return [self.embed(text) for text in texts]
