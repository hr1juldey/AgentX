"""Mem0AI client wrapper for AGENTX.

Provides AGENTX-specific interface to Mem0AI long-term memory.

Uses local Ollama for embeddings and Qdrant for vector storage.
No API keys required for fully local setup.
"""

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

from agentx.infrastructure.memory.mem0.config import build_mem0_config
from agentx.infrastructure.memory.mem0.result_parser import (
    parse_search_results,
)

logger = logging.getLogger(__name__)


class Mem0Client:
    """Wrapper for Mem0AI memory client.

    Provides simplified interface for storing and searching conversation memories.
    """

    def __init__(
        self,
        qdrant_host: str,
        qdrant_port: int,
        llm_model: str,
        embedder_model: str,
        embedding_dims: int,
    ) -> None:
        """Initialize the Mem0AI client with local Ollama + Qdrant.

        Args:
            qdrant_host: Qdrant server host
            qdrant_port: Qdrant server port
            llm_model: Ollama LLM model name
            embedder_model: Ollama embedding model name
            embedding_dims: Embedding vector dimensions
        """
        from mem0 import Memory

        config = build_mem0_config(
            qdrant_host=qdrant_host,
            qdrant_port=qdrant_port,
            llm_model=llm_model,
            embedder_model=embedder_model,
            embedding_dims=embedding_dims,
        )

        self._memory = Memory.from_config(config)
        logger.info(
            f"Mem0AI initialized: qdrant={qdrant_host}:{qdrant_port}, "
            f"llm={llm_model}, embedder={embedder_model}, dims={embedding_dims}"
        )

    async def search_memory(
        self, query: str, user_id: str, limit: int = 5
    ) -> list[str]:
        """Search memories for relevant context.

        Args:
            query: Search query text
            user_id: User identifier for memory isolation
            limit: Maximum number of results

        Returns:
            List of memory texts (sorted by relevance)
        """
        try:
            results = self._memory.search(
                query=query,
                user_id=user_id,
                limit=limit,
            )

            memories = parse_search_results(results)

            logger.debug(
                f"Mem0AI search: query='{query[:30]}...', user_id={user_id}, "
                f"found={len(memories)} results"
            )

            return memories

        except Exception as e:
            logger.error(f"Mem0AI search failed: {e}")
            return []

    async def store_memory(
        self, text: str, user_id: str, metadata: dict | None = None
    ) -> None:
        """Store interaction in memory.

        Args:
            text: Interaction text to store
            user_id: User identifier for memory isolation
            metadata: Optional metadata dict (category, timestamp, etc.)
        """
        try:
            self._memory.add(
                text,  # positional argument
                user_id=user_id,
                metadata=metadata or {},
            )

            logger.debug(f"Mem0AI store: text='{text[:50]}...', user_id={user_id}")

        except Exception as e:
            logger.error(f"Mem0AI store failed: {e}")

    async def add(self, messages: list[dict], user_id: str) -> dict:
        """Store interaction in memory (legacy interface).

        Args:
            messages: List of message dicts with role and content
            user_id: User identifier

        Returns:
            Storage result dict
        """
        # Format messages as text for storage
        text_parts: list[str] = []
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            text_parts.append(f"{role}: {content}")  # type: ignore[list-item]

        text = "\n".join(text_parts)

        await self.store_memory(
            text=text,
            user_id=user_id,
            metadata={"type": "conversation"},
        )

        return {"status": "stored", "count": len(messages)}
