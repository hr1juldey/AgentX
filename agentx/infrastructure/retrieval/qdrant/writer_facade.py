"""Qdrant collection writer facade.

Provides batch and single insert methods for QdrantCollectionManager.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from agentx.infrastructure.retrieval.qdrant.writer import (
    insert_document as _insert_document,
    insert_documents_batch as _insert_documents_batch,
)

if TYPE_CHECKING:
    pass


class CollectionWriterMixin:
    """Mixin class for document insert operations."""

    def insert_document(
        self,
        document_id: str,
        text: str,
        dense_vector: list[float],
        colbert_vector: list[list[float]] | None = None,
        metadata: dict | None = None,
        timeout: float | None = None,
    ) -> bool:
        """Insert a document with both dense and ColBERT vectors."""
        return _insert_document(
            self._client,  # type: ignore[attr-defined]
            self.collection_name,  # type: ignore[attr-defined]
            document_id,
            text,
            dense_vector,
            colbert_vector,
            metadata,
            timeout,
        )

    def insert_documents_batch(
        self,
        documents: list[dict],
        timeout: float | None = None,
        batch_size: int = 100,
    ) -> int:
        """Insert multiple documents in batches for efficiency."""
        return _insert_documents_batch(
            self._client,  # type: ignore[attr-defined]
            self.collection_name,  # type: ignore[attr-defined]
            documents,
            timeout,
            batch_size,
        )
