"""Memory agent for RAG operations.

Retrieves relevant context from QdrantVectorStore using ColBERTv2 embeddings.

Phase 3 Fix: Converted async forward() to sync for DSPy compatibility.
"""

import asyncio

import dspy

from agentx.infrastructure.database.qdrant.qdrant_vector_store import QdrantVectorStore


class MemoryAgent(dspy.Module):
    """Memory agent using QdrantVectorStore for real retrieval (ColBERTv2-powered).

    Fraud #2 fix: Uses real QdrantVectorStore search instead of dspy.Predict fake retrieval.

    Architecture Note: QdrantVectorStore handles retrieval with ColBERTv2.
    Mem0 is used for memory management only (consolidation, categorization, TTL).

    Phase 3 Fix: Now uses sync forward() for DSPy compatibility.
    """

    def __init__(self) -> None:
        """Initialize the memory agent with QdrantVectorStore."""
        super().__init__()
        self.vector_store = QdrantVectorStore()

    def forward(
        self, query: str, session_id: str, user_id: str = "default"
    ) -> dspy.Prediction:
        """Retrieve relevant context from QdrantVectorStore (real retrieval).

        Phase 3 Fix: Converted from async to sync for DSPy compatibility.
        DSPy does not support async forward() methods.

        Args:
            query: User's question or request.
            session_id: Current session identifier.
            user_id: User ID for memory lookup (default: "default").

        Returns:
            dspy.Prediction: Retrieved context with source references.
        """
        # Run async search_memories in event loop
        memories = asyncio.run(
            self.vector_store.search_memories(
                query=query,
                user_id=user_id,
                limit=10,
            )
        )

        # Format context from memories
        context = "\n".join([m.get("content", "") for m in memories])
        sources = [str(m.get("metadata", {}).get("memory_id", "")) for m in memories]

        return dspy.Prediction(
            context=context,
            sources=sources,
            retrieval_count=len(memories),
        )


__all__ = ["MemoryAgent"]
