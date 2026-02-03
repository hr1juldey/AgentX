"""Memory agent for RAG operations.

Retrieves relevant context from QdrantVectorStore using ColBERTv2 embeddings.
"""

import dspy

from agentx.infrastructure.database.qdrant.qdrant_vector_store import QdrantVectorStore


class MemoryAgent(dspy.Module):
    """Memory agent using QdrantVectorStore for real retrieval (ColBERTv2-powered).

    Fraud #2 fix: Uses real QdrantVectorStore search instead of dspy.Predict fake retrieval.

    Architecture Note: QdrantVectorStore handles retrieval with ColBERTv2.
    Mem0 is used for memory management only (consolidation, categorization, TTL).
    """

    def __init__(self) -> None:
        """Initialize the memory agent with QdrantVectorStore."""
        super().__init__()
        self.vector_store = QdrantVectorStore()

    async def forward(
        self, query: str, session_id: str, user_id: str = "default"
    ) -> dspy.Prediction:
        """Retrieve relevant context from QdrantVectorStore (real retrieval).

        Args:
            query: User's question or request.
            session_id: Current session identifier.
            user_id: User ID for memory lookup (default: "default").

        Returns:
            dspy.Prediction: Retrieved context with source references.
        """
        # REAL QdrantVectorStore search (uses ColBERTv2 via ColBERTEmbedder)
        memories = await self.vector_store.search_memories(
            query=query,
            user_id=user_id,
            limit=10,
        )

        # Format context from memories
        context = "\n".join([m.get("content", "") for m in memories])
        sources = [str(m.get("metadata", {}).get("memory_id", "")) for m in memories]

        return dspy.Prediction(
            context=context,
            sources=sources,
            retrieval_count=len(memories),
        )
