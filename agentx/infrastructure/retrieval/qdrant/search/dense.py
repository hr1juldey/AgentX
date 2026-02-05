"""Qdrant dense-only search operations."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from agentx.infrastructure.retrieval.qdrant.constants import DENSE_VECTOR_NAME

if TYPE_CHECKING:
    from qdrant_client import QdrantClient

logger = logging.getLogger(__name__)


def search_dense(
    client: QdrantClient,
    collection_name: str,
    query_vector: list[float],
    limit: int = 100,
) -> list[dict]:
    """Search using dense vector only.

    Args:
        client: Qdrant client instance
        collection_name: Name of the collection
        query_vector: Dense query embedding
        limit: Number of results to return

    Returns:
        List of search results with payload
    """
    try:
        results = client.query_points(
            collection_name=collection_name,
            query=query_vector,
            using=DENSE_VECTOR_NAME,
            limit=limit,
            with_payload=True,
        )

        # Extract results with safe payload access
        output = []
        for hit in results.points:
            payload = (
                hit.payload
                if hasattr(hit, "payload") and hit.payload is not None
                else {}
            )
            output.append(
                {
                    "id": hit.id,
                    "score": hit.score,
                    "payload": payload,
                    "text": payload.get("text", "")
                    if isinstance(payload, dict)
                    else "",
                }
            )
        return output

    except Exception as e:
        logger.error(f"Dense search failed: {e}")
        return []
