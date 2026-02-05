"""Qdrant collection management for named vector configurations.

Manages Qdrant collections with support for multiple named vectors
(dense embeddings and ColBERT multi-vectors).

Supports both per-agent private collections and shared knowledge collections.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from agentx.infrastructure.retrieval.qdrant.collection import (
    create_collection,
    validate_collection,
)
from agentx.infrastructure.retrieval.qdrant.constants import (
    COLBERT_VECTOR_NAME,
    DENSE_VECTOR_NAME,
)
from agentx.infrastructure.retrieval.qdrant.search_facade import (
    CollectionSearchMixin,
)
from agentx.infrastructure.retrieval.qdrant.writer_facade import (
    CollectionWriterMixin,
)

if TYPE_CHECKING:
    from qdrant_client import QdrantClient

logger = logging.getLogger(__name__)


class QdrantCollectionManager(CollectionWriterMixin, CollectionSearchMixin):
    """Manager for Qdrant collections with named vectors.

    Handles collection creation, validation, and configuration for
    storing both dense and ColBERT embeddings in the same collection.

    Supports per-agent collections and shared knowledge collections.
    """

    # Vector name constants (same across all collections)
    DENSE_VECTOR_NAME = DENSE_VECTOR_NAME
    COLBERT_VECTOR_NAME = COLBERT_VECTOR_NAME

    def __init__(self, qdrant_client: QdrantClient, collection_name: str) -> None:
        """Initialize the collection manager.

        Args:
            qdrant_client: Qdrant client instance
            collection_name: Name of the collection (e.g., "research_agent_memory",
                           "chatbot_agent_memory", or "agentx_knowledge" for shared)
        """
        self._client = qdrant_client
        self.collection_name = collection_name

        logger.info(
            f"QdrantCollectionManager initialized for collection: {collection_name}"
        )

    def ensure_collection_exists(self, force_recreate: bool = False) -> bool:
        """Ensure the collection exists with proper configuration.

        Creates the collection if it doesn't exist, or validates
        configuration if it does.

        Args:
            force_recreate: If True, delete and recreate existing collection

        Returns:
            True if collection is ready, False otherwise
        """
        try:
            # Check if collection exists
            collections = self._client.get_collections()
            collection_names = {col.name for col in collections.collections}

            if self.collection_name in collection_names:
                if force_recreate:
                    logger.info(f"Force recreating collection '{self.collection_name}'")
                    self.delete_collection()
                    return create_collection(self._client, self.collection_name)
                else:
                    logger.info(f"Collection '{self.collection_name}' already exists")
                    return validate_collection(self._client, self.collection_name)
            else:
                return create_collection(self._client, self.collection_name)

        except Exception as e:
            logger.error(f"Failed to ensure collection exists: {e}")
            return False

    def delete_collection(self) -> bool:
        """Delete the collection (use with caution).

        Returns:
            True if successful, False otherwise
        """
        try:
            self._client.delete_collection(self.collection_name)
            logger.info(f"Deleted collection '{self.collection_name}'")
            return True
        except Exception as e:
            logger.error(f"Failed to delete collection: {e}")
            return False
