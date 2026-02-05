"""Qdrant collection search facade.

Provides search methods for QdrantCollectionManager.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from agentx.infrastructure.retrieval.qdrant.search import (
    search_dense as _search_dense,
    search_with_prefetch as _search_with_prefetch,
)

if TYPE_CHECKING:
    pass


class CollectionSearchMixin:
    """Mixin class for search operations."""

    def search_with_prefetch(
        self,
        dense_query: list[float],
        colbert_query: list[list[float]],
        limit: int = 5,
        prefetch_limit: int = 100,
    ) -> list[dict]:
        """Search using prefetch pattern: dense retrieve, ColBERT rerank."""
        return _search_with_prefetch(
            self._client,  # type: ignore[attr-defined]
            self.collection_name,  # type: ignore[attr-defined]
            dense_query,
            colbert_query,
            limit,
            prefetch_limit,
        )

    def search_dense(self, query_vector: list[float], limit: int = 100) -> list[dict]:
        """Search using dense vector only."""
        return _search_dense(
            self._client,  # type: ignore[attr-defined]
            self.collection_name,  # type: ignore[attr-defined]
            query_vector,
            limit,
        )
