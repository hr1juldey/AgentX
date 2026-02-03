"""DSPy retriever that wraps Mem0 for consistent ColBERTv2 embeddings.

Uses Mem0's search which already uses ColBERTv2 via QdrantVectorStore.
This ensures DSPy, Mem0, and Qdrant all use the SAME embeddings.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class RetrievedMemory:
    """A retrieved memory formatted for DSPy."""

    long_text: str
    score: float
    metadata: dict[str, Any]


class Mem0DSPyRetriever:
    """DSPy-compatible retriever wrapping Mem0.

    Uses Mem0's search which already uses ColBERTv2 via QdrantVectorStore.
    This ensures DSPy, Mem0, and Qdrant all use the SAME embeddings.
    """

    def __init__(
        self, k: int = 20, quality_threshold: float = 0.6, min_results: int = 3
    ):
        """Initialize retriever with quality-based filtering.

        Args:
            k: Max candidates to retrieve from Mem0
            quality_threshold: Stop retrieving if score drops below this
            min_results: Always return at least this many results
        """
        self.k = k
        self.quality_threshold = quality_threshold
        self.min_results = min_results

    async def __call__(
        self,
        query: str,
        k: int | None = None,
        user_id: str = "default_user",
        **kwargs: Any,
    ) -> list[RetrievedMemory]:
        """Retrieve memories using Mem0's ColBERTv2-powered search.

        Args:
            query: Search query
            k: Number of results (overrides default)
            user_id: User to retrieve memories for
            **kwargs: Additional arguments

        Returns:
            List of retrieved memories filtered by quality
        """
        from agentx.infrastructure.memory.mem0_adapter import Mem0MemoryAdapter

        k = k or self.k
        mem0_adapter = Mem0MemoryAdapter()

        # Call Mem0's search (uses ColBERTv2 via QdrantVectorStore)
        memories = await mem0_adapter.search_memories(
            query=query,
            user_id=user_id,
            limit=k,
        )

        # Filter by quality score (adaptive retrieval)
        results = []
        for i, mem in enumerate(memories):
            score = mem.get("score", 0.0)
            content = mem.get("content", "")

            # Always include at least min_results
            if i < self.min_results or score >= self.quality_threshold:
                results.append(
                    RetrievedMemory(
                        long_text=content,
                        score=score,
                        metadata=mem.get("metadata", {}),
                    )
                )

        return results

    def retrieve_sync(
        self, query: str, k: int | None = None, **kwargs: Any
    ) -> list[RetrievedMemory]:
        """Synchronous wrapper for DSPy compatibility.

        DSPy may call this synchronously, so we need to handle it.
        """
        import asyncio

        return asyncio.run(self.__call__(query=query, k=k, **kwargs))
