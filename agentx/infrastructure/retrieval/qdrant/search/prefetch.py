"""Qdrant prefetch search (dense retrieve + ColBERT rerank)."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from agentx.infrastructure.retrieval.qdrant.constants import (
    COLBERT_VECTOR_NAME,
    DENSE_VECTOR_NAME,
)

if TYPE_CHECKING:
    from qdrant_client import QdrantClient

logger = logging.getLogger(__name__)


def search_with_prefetch(
    client: QdrantClient,
    collection_name: str,
    dense_query: list[float],
    colbert_query: list[list[float]],
    limit: int = 5,
    prefetch_limit: int = 100,
) -> list[dict]:
    """Search using prefetch pattern: dense retrieve, ColBERT rerank.

    This is the recommended pattern from Qdrant medical bot example.

    Args:
        client: Qdrant client instance
        collection_name: Name of the collection
        dense_query: Dense query embedding for initial retrieval
        colbert_query: ColBERT query multivector for reranking
        limit: Number of final results to return
        prefetch_limit: Number of candidates to retrieve with dense

    Returns:
        List of search results with payload
    """
    try:
        from qdrant_client.models import Prefetch

        # Prefetch pattern: retrieve with dense, rerank with ColBERT
        results = client.query_points(
            collection_name=collection_name,
            prefetch=[
                Prefetch(
                    query=dense_query,
                    using=DENSE_VECTOR_NAME,
                    limit=prefetch_limit,
                )
            ],
            query=colbert_query,
            using=COLBERT_VECTOR_NAME,
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
        logger.error(f"Prefetch search failed: {e}")
        return []
