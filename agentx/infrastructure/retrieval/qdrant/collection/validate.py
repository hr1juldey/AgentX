"""Qdrant collection validation logic."""

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


def validate_collection(
    client: QdrantClient,
    collection_name: str,
) -> bool:
    """Validate existing collection configuration.

    Args:
        client: Qdrant client instance
        collection_name: Name of the collection to validate

    Returns:
        True if configuration is valid, False otherwise
    """
    try:
        collection_info = client.get_collection(collection_name)

        # Check for named vectors (dict type in new API)
        vectors_config = collection_info.config.params.vectors
        if not isinstance(vectors_config, dict):
            logger.warning(
                f"Collection '{collection_name}' exists but "
                "doesn't have named vectors configured"
            )
            return False

        vector_names = list(vectors_config.keys())

        # Verify required vectors exist
        has_dense = DENSE_VECTOR_NAME in vector_names
        has_colbert = COLBERT_VECTOR_NAME in vector_names

        if not has_dense or not has_colbert:
            logger.warning(
                f"Collection '{collection_name}' missing required vectors. "
                f"Has: {vector_names}, Required: "
                f"[{DENSE_VECTOR_NAME}, {COLBERT_VECTOR_NAME}]"
            )
            return False

        logger.info(f"Collection '{collection_name}' validated successfully")
        return True

    except Exception as e:
        logger.error(f"Failed to validate collection: {e}")
        return False
