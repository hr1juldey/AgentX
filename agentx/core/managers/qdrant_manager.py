"""Qdrant client and collection manager management."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from agentx.infrastructure.retrieval.qdrant_collection_manager import (
        QdrantCollectionManager,
    )

logger = logging.getLogger(__name__)

_qdrant_client: Optional[object] = None
# Cache of collection managers by collection name
_qdrant_collection_managers: dict[str, QdrantCollectionManager] = {}


def get_qdrant_client() -> object:
    """Get the singleton Qdrant client.

    Returns:
        QdrantClient instance for vector operations
    """
    from qdrant_client import QdrantClient
    from qdrant_client.http.exceptions import UnexpectedResponse

    global _qdrant_client
    if _qdrant_client is None:
        from agentx.core.config import settings

        try:
            _qdrant_client = QdrantClient(
                host=settings.qdrant_host,
                port=settings.qdrant_port,
                timeout=600,
            )
            # Verify connection
            collections = _qdrant_client.get_collections()
            logger.info(
                f"Qdrant client initialized: {settings.qdrant_host}:{settings.qdrant_port}, "
                f"{len(collections.collections)} collections"
            )
        except UnexpectedResponse as e:
            logger.warning(f"Qdrant client initialization failed: {e}")
            logger.info("Continuing without Qdrant client")
            _qdrant_client = None
        except Exception as e:
            logger.warning(f"Qdrant client connection failed: {e}")
            logger.info("Continuing without Qdrant client")
            _qdrant_client = None
    return _qdrant_client


def get_qdrant_collection_manager(
    collection_name: str = "agentx_knowledge",
) -> Optional[QdrantCollectionManager]:
    """Get or create a Qdrant collection manager for a specific collection.

    Supports per-agent private collections and shared knowledge collections.
    Collection managers are cached by collection name.

    Args:
        collection_name: Name of the collection (e.g., "research_agent_memory",
                       "chatbot_agent_memory", or "agentx_knowledge" for shared)

    Returns:
        QdrantCollectionManager instance or None if Qdrant unavailable

    Examples:
        # Get shared knowledge collection
        shared_manager = get_qdrant_collection_manager("agentx_knowledge")

        # Get per-agent private collection
        research_manager = get_qdrant_collection_manager("research_agent_memory")
        chatbot_manager = get_qdrant_collection_manager("chatbot_agent_memory")
    """
    from agentx.infrastructure.retrieval.qdrant_collection_manager import (
        QdrantCollectionManager,
    )

    global _qdrant_collection_managers

    # Return cached manager if exists
    if collection_name in _qdrant_collection_managers:
        return _qdrant_collection_managers[collection_name]

    # Get Qdrant client
    qdrant_client = get_qdrant_client()
    if qdrant_client is None:
        logger.warning(
            f"Qdrant client unavailable, cannot create collection manager for '{collection_name}'"
        )
        return None

    try:
        manager = QdrantCollectionManager(
            qdrant_client,  # type: ignore[arg-type]
            collection_name,
        )
        # Ensure collection exists with proper configuration
        if manager.ensure_collection_exists():
            logger.info(
                f"QdrantCollectionManager initialized for '{collection_name}' and collection ready"
            )
        else:
            logger.warning(
                f"QdrantCollectionManager initialized for '{collection_name}' but collection validation failed"
            )
        # Cache the manager
        _qdrant_collection_managers[collection_name] = manager
        return manager
    except Exception as e:
        logger.warning(
            f"QdrantCollectionManager initialization failed for '{collection_name}': {e}"
        )
        return None
