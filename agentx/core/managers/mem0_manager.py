"""Mem0AI client management."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

from agentx.core.config import settings

if TYPE_CHECKING:
    from agentx.infrastructure.memory.mem0_client import Mem0Client

logger = logging.getLogger(__name__)

_mem0_client: Optional[Mem0Client] = None


def get_mem0_client() -> Optional[Mem0Client]:
    """Get the singleton Mem0AI client.

    Uses local Ollama for LLM/embeddings and Qdrant for vector storage.
    No API keys required.

    Returns:
        Mem0Client instance or None if unavailable
    """
    from agentx.infrastructure.memory.mem0_client import Mem0Client

    global _mem0_client
    if _mem0_client is None:
        try:
            _mem0_client = Mem0Client(
                qdrant_host=settings.mem0_qdrant_host,
                qdrant_port=settings.mem0_qdrant_port,
                llm_model=settings.mem0_llm_model,
                embedder_model=settings.mem0_embedder_model,
                embedding_dims=settings.mem0_embedding_dims,
            )
            logger.info("Mem0AI client initialized")
        except Exception as e:
            logger.warning(f"Mem0AI client initialization failed: {e}")
            logger.info("Continuing without persistent memory")
            _mem0_client = None

    return _mem0_client
