"""Prefetch RM wrapper - dense (fast) → ColBERT (accurate) pattern."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import dspy
from dspy.retrievers import Retrieve  # type: ignore[import]

if TYPE_CHECKING:
    from agentx.infrastructure.retrieval.colbert_vectorizer import ColBERTVectorizer
    from agentx.infrastructure.retrieval.dense_vectorizer import DenseVectorizer

logger = logging.getLogger(__name__)


class PrefetchRM(Retrieve):
    """Retriever with prefetch: dense for speed, ColBERT for accuracy.

    Implements the Qdrant medical bot prefetch pattern:
    1. Use dense embeddings to quickly retrieve top-100 candidates
    2. Re-rank candidates with ColBERT multi-vectors in ONE query
    3. Return final top-k results as DSPy Prediction

    This combines the speed of dense embeddings with the accuracy of ColBERT
    using Qdrant's native query_points with Prefetch.

    Usage in DSPy:
        self.prefetch_retrieve = PrefetchRM(...)
        result = self.prefetch_retrieve(query)
        passages = result.passages  # DSPy-compatible!
    """

    def __init__(
        self,
        collection_manager,
        dense_vectorizer: DenseVectorizer,
        colbert_vectorizer: ColBERTVectorizer,
        k: int = 5,
    ) -> None:
        """Initialize the prefetch retriever.

        Args:
            collection_manager: QdrantCollectionManager instance
            dense_vectorizer: DenseVectorizer instance (Ollama)
            colbert_vectorizer: ColBERTVectorizer instance (FastEmbed)
            k: Default number of results to return
        """
        self._collection_manager = collection_manager
        self._dense_vectorizer = dense_vectorizer
        self._colbert_vectorizer = colbert_vectorizer
        self.k = k

        logger.info(
            f"PrefetchRM initialized: collection={collection_manager.COLLECTION_NAME}, "
            f"dense_vector={collection_manager.DENSE_VECTOR_NAME}, "
            f"colbert_vector={collection_manager.COLBERT_VECTOR_NAME}, k={k}"
        )

    def forward(  # type: ignore[override]
        self, query: str, k: int | None = None, **kwargs: object
    ) -> dspy.Prediction:
        """Retrieve relevant documents with prefetch fallback.

        Args:
            query: Search query
            k: Number of results to return
            **kwargs: Additional arguments for parent class compatibility

        Returns:
            DSPy Prediction object with passages attribute
        """
        if k is None:
            k = self.k

        try:
            # Embed query with both vectorizers
            dense_query = self._dense_vectorizer.embed(query)

            # Try ColBERT with prefetch if available
            if self._colbert_vectorizer.is_available:
                colbert_query = self._colbert_vectorizer.query_embed(query)
                if colbert_query:
                    # Use prefetch pattern: dense retrieve, ColBERT rerank
                    results = self._collection_manager.search_with_prefetch(
                        dense_query=dense_query,
                        colbert_query=colbert_query,
                        limit=k,
                        prefetch_limit=100,
                    )
                    passages = [r.get("text", "") for r in results]
                    return dspy.Prediction(passages=passages)

            # Fallback: dense-only search
            results = self._collection_manager.search_dense(
                query_vector=dense_query, limit=k
            )
            passages = [r.get("text", "") for r in results]
            return dspy.Prediction(passages=passages)

        except Exception as e:
            logger.error(f"PrefetchRM retrieval failed: {e}")
            return dspy.Prediction(passages=[])
