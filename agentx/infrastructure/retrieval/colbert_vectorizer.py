"""ColBERT vectorizer for multi-vector embeddings using FastEmbed.

Uses FastEmbed's LateInteractionTextEmbedding for ColBERTv2 multi-vectors.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class ColBERTVectorizer:
    """ColBERT vectorizer using FastEmbed.

    Uses FastEmbed's LateInteractionTextEmbedding to produce
    multi-vector ColBERTv2 embeddings for accurate reranking.

    FastEmbed is lightweight and has no external dependencies.
    """

    def __init__(self, model_name: str = "colbert-ir/colbertv2.0") -> None:
        """Initialize the ColBERT vectorizer.

        Args:
            model_name: ColBERT model name (default: colbert-ir/colbertv2.0)
        """
        self.model_name = model_name
        self._model = None
        self._available = False

        try:
            from fastembed import LateInteractionTextEmbedding

            self._model = LateInteractionTextEmbedding(model_name)
            self._available = True
            logger.info(f"ColBERTVectorizer using FastEmbed: {model_name}")
        except ImportError:
            logger.warning(
                "FastEmbed not installed. Install with: pip install fastembed"
            )
        except Exception as e:
            logger.warning(f"FastEmbed ColBERT initialization failed: {e}")

    def embed(self, text: str) -> "list[list[float]]":
        """Convert text to multi-vector ColBERT embedding.

        Args:
            text: Input text to embed

        Returns:
            List of vectors (each token gets a 128-dim vector)
            Returns empty list if FastEmbed is not available
        """
        if not self._available or self._model is None:
            return []

        try:
            # FastEmbed returns generator, convert to list
            result = list(self._model.embed([text]))
            if result and len(result) > 0:
                # Result is shape (N, 128) where N is number of tokens
                embedding = result[0]
                # Convert to list of lists for Qdrant multivector
                if hasattr(embedding, "tolist"):
                    return embedding.tolist()
                return list(embedding)
            return []
        except Exception as e:
            logger.warning(f"ColBERT embedding failed: {e}")
            return []

    def query_embed(self, text: str) -> "list[list[float]]":
        """Embed query text for ColBERT retrieval.

        Args:
            text: Query text to embed

        Returns:
            List of token vectors for the query
        """
        if not self._available or self._model is None:
            return []

        try:
            # Use query_embed for queries if available (same as embed for FastEmbed)
            result = list(self._model.query_embed([text]))
            if result and len(result) > 0:
                embedding = result[0]
                if hasattr(embedding, "tolist"):
                    return embedding.tolist()
                return list(embedding)
            return []
        except AttributeError:
            # Fall back to embed if query_embed not available
            return self.embed(text)
        except Exception as e:
            logger.warning(f"ColBERT query embedding failed: {e}")
            return []

    @property
    def dimension(self) -> int:
        """Get the embedding vector dimension.

        Returns:
            Size of each token vector (128 for colbertv2.0)
        """
        return 128

    def embed_batch(self, texts: "list[str]") -> "list[list[list[float]]]":
        """Embed multiple texts.

        Args:
            texts: List of input texts to embed

        Returns:
            List of multi-vector embeddings (one per text)
        """
        if not self._available or self._model is None:
            return [[] for _ in texts]

        try:
            results = list(self._model.embed(texts))
            output = []
            for emb in results:
                if hasattr(emb, "tolist"):
                    output.append(emb.tolist())
                else:
                    output.append(list(emb))
            return output
        except Exception as e:
            logger.warning(f"Batch ColBERT embedding failed: {e}")
            return [[] for _ in texts]

    @property
    def is_available(self) -> bool:
        """Check if ColBERT vectorizer is available.

        Returns:
            True if FastEmbed is available, False otherwise
        """
        return self._available
