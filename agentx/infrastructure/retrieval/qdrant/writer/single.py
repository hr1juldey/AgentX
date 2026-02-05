"""Qdrant single document insert operation."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from qdrant_client.models import PointStruct

from agentx.infrastructure.retrieval.qdrant.constants import (
    COLBERT_VECTOR_NAME,
    DENSE_VECTOR_NAME,
)

if TYPE_CHECKING:
    from qdrant_client import QdrantClient

logger = logging.getLogger(__name__)


def insert_document(
    client: QdrantClient,
    collection_name: str,
    document_id: str,
    text: str,
    dense_vector: list[float],
    colbert_vector: list[list[float]] | None = None,
    metadata: dict | None = None,
    timeout: float | None = None,
) -> bool:
    """Insert a document with both dense and ColBERT vectors.

    Args:
        client: Qdrant client instance
        collection_name: Name of the collection
        document_id: Unique document identifier
        text: Document text content
        dense_vector: Dense embedding vector
        colbert_vector: ColBERT multi-vector (optional)
        metadata: Additional metadata payload
        timeout: Request timeout in seconds (defaults to client timeout)

    Returns:
        True if successful, False otherwise
    """
    try:
        # Prepare vectors dict
        vectors: dict[str, object] = {
            DENSE_VECTOR_NAME: dense_vector,
        }

        # Add ColBERT multivector if provided
        if colbert_vector:
            vectors[COLBERT_VECTOR_NAME] = colbert_vector

        # Prepare payload
        payload = {
            "text": text,
            "metadata": metadata or {},
        }

        # Create point and insert
        # Note: timeout is configured at client level, not per-operation
        point = PointStruct(
            id=document_id,
            vector=vectors,
            payload=payload,
        )
        client.upsert(
            collection_name=collection_name,
            points=[point],
        )

        logger.debug(
            f"Inserted document '{document_id}' in '{collection_name}' "
            f"with {len(vectors)} vectors"
        )
        return True

    except Exception as e:
        logger.error(f"Failed to insert document: {e}")
        return False
