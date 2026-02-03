"""Memory agent for RAG operations.

Retrieves relevant context from memory stores via Mem0 (ColBERTv2-powered).
"""

import dspy

from agentx.infrastructure.memory.mem0_adapter import Mem0MemoryAdapter


class MemoryAgent(dspy.Module):
    """Memory agent using Mem0 for real retrieval (ColBERTv2-powered).

    Fraud #2 fix: Uses real Mem0 search instead of dspy.Predict fake retrieval.
    """

    def __init__(self) -> None:
        """Initialize the memory agent with Mem0 adapter."""
        super().__init__()
        self.mem0_adapter = Mem0MemoryAdapter()

    async def forward(
        self, query: str, session_id: str, user_id: str = "default"
    ) -> dspy.Prediction:
        """Retrieve relevant context from Mem0 (real retrieval).

        Args:
            query: User's question or request.
            session_id: Current session identifier.
            user_id: User ID for memory lookup (default: "default").

        Returns:
            dspy.Prediction: Retrieved context with source references.
        """
        # REAL Mem0 search (uses ColBERTv2 via QdrantVectorStore)
        memories = await self.mem0_adapter.search_memories(
            query=query,
            user_id=user_id,
            limit=10,
        )

        # Format context from memories
        context = "\n".join([m.get("memory", "") for m in memories])
        sources = [str(m.get("metadata", {}).get("memory_id", "")) for m in memories]

        return dspy.Prediction(
            context=context,
            sources=sources,
        )
