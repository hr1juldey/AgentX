"""Qdrant batch document insert operations."""

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


def insert_documents_batch(
    client: QdrantClient,
    collection_name: str,
    documents: list[dict],
    timeout: float | None = None,
    batch_size: int = 100,
) -> int:
    """Insert multiple documents in batches for efficiency.

    Args:
        client: Qdrant client instance
        collection_name: Name of the collection
        documents: List of document dicts with keys:
            - id: Unique document identifier
            - text: Document text content
            - dense_vector: Dense embedding vector
            - colbert_vector: ColBERT multi-vector (optional)
            - metadata: Additional metadata payload (optional)
        timeout: Request timeout in seconds per batch
        batch_size: Number of documents per batch

    Returns:
        Number of successfully inserted documents
    """
    inserted_count = 0
    for i in range(0, len(documents), batch_size):
        batch = documents[i : i + batch_size]
        points = []
        for doc in batch:
            vectors: dict[str, object] = {
                DENSE_VECTOR_NAME: doc["dense_vector"],
            }
            if doc.get("colbert_vector"):
                vectors[COLBERT_VECTOR_NAME] = doc["colbert_vector"]

            point = PointStruct(
                id=doc["id"],
                vector=vectors,
                payload={
                    "text": doc["text"],
                    "metadata": doc.get("metadata", {}),
                },
            )
            points.append(point)

        try:
            # Note: timeout is configured at client level, not per-operation
            client.upsert(
                collection_name=collection_name,
                points=points,
            )
            inserted_count += len(points)
            logger.debug(
                f"Inserted batch {i // batch_size + 1}: "
                f"{len(points)} documents in '{collection_name}'"
            )
        except Exception as e:
            logger.error(f"Failed to insert batch {i // batch_size + 1}: {e}")

    logger.info(
        f"Batch insert complete: {inserted_count}/{len(documents)} "
        f"documents inserted in '{collection_name}'"
    )
    return inserted_count
