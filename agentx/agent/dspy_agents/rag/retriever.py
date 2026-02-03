"""RAG retrieval module for context retrieval from Mem0.

Phase 3 Fix: Extracted from RAGContextGenerator for SRP compliance.
"""

import asyncio

from agentx.infrastructure.retrieval.mem0_dspy_retriever import Mem0DSPyRetriever


class RealRetriever:
    """Handles REAL retrieval from Mem0 using ColBERTv2-powered Qdrant.

    Phase 3 Fix: Extracted from RAGContextGenerator.
    Single Responsibility: Retrieve relevant memories.
    """

    def __init__(
        self,
        k: int = 10,
        quality_threshold: float = 0.6,
        min_results: int = 3,
    ) -> None:
        """Initialize the retriever with Mem0DSPyRetriever.

        Args:
            k: Maximum number of results to retrieve
            quality_threshold: Minimum score threshold (0.0-1.0)
            min_results: Minimum results to return regardless of threshold
        """
        self._retriever = Mem0DSPyRetriever(
            k=k,
            quality_threshold=quality_threshold,
            min_results=min_results,
        )

    def retrieve(
        self,
        query: str,
        user_id: str = "default_user",
    ) -> list[str]:
        """Retrieve relevant memories for a query.

        Phase 3 Fix: Now sync, compatible with updated Mem0DSPyRetriever.

        Args:
            query: User query to retrieve context for
            user_id: User to retrieve memories for

        Returns:
            List of retrieved memory texts (filtered by quality)
        """
        # Run async retrieval in event loop
        results = asyncio.run(
            self._retriever(query=query, k=self._retriever.k, user_id=user_id)
        )
        return results


__all__ = ["RealRetriever"]
