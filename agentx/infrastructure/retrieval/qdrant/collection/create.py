"""Qdrant collection creation logic."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from qdrant_client.models import (
    HnswConfigDiff,
    MultiVectorConfig,
    MultiVectorComparator,
    VectorParams,
)

from agentx.infrastructure.retrieval.qdrant.constants import (
    COLBERT_DIM,
    COLBERT_VECTOR_NAME,
    DENSE_DIM,
    DENSE_DISTANCE,
    DENSE_VECTOR_NAME,
)

if TYPE_CHECKING:
    from qdrant_client import QdrantClient

logger = logging.getLogger(__name__)


def create_collection(
    client: QdrantClient,
    collection_name: str,
) -> bool:
    """Create a new collection with named vectors.

    Args:
        client: Qdrant client instance
        collection_name: Name of the collection to create

    Returns:
        True if successful, False otherwise
    """
    try:
        # Configure named vectors as dict (medical bot pattern)
        vectors_config = {
            # Dense vector for fast retrieval (indexed with COSINE distance)
            DENSE_VECTOR_NAME: VectorParams(
                size=DENSE_DIM,
                distance=DENSE_DISTANCE,
                # HNSW indexing by default for fast search
            ),
            # ColBERT multivector for reranking (NOT indexed, uses MAX_SIM)
            COLBERT_VECTOR_NAME: VectorParams(
                size=COLBERT_DIM,
                distance=DENSE_DISTANCE,  # Required for token-level comparison
                multivector_config=MultiVectorConfig(
                    comparator=MultiVectorComparator.MAX_SIM  # Max aggregation
                ),
                hnsw_config=HnswConfigDiff(m=0),  # NO indexing for reranker!
            ),
        }

        # Create collection
        client.create_collection(
            collection_name=collection_name,
            vectors_config=vectors_config,
        )

        logger.info(
            f"Created collection '{collection_name}' with "
            f"named vectors: {DENSE_VECTOR_NAME} ({DENSE_DIM}D), "
            f"{COLBERT_VECTOR_NAME} ({COLBERT_DIM}D multivector)"
        )
        return True

    except Exception as e:
        logger.error(f"Failed to create collection: {e}")
        return False
