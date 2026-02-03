"""Main DSPy ReAct agent.

Implements the primary agent using DSPy ReAct pattern.
Enhanced with QdrantVectorStore pre-retrieval for user history context.

Phase 3 Fix: Converted async forward() to sync for DSPy compatibility.
"""

import asyncio

import dspy

from agentx.agent.dspy_signatures.main_signatures import MainAgentSignature
from agentx.agent.tools.main_tools import AVAILABLE_TOOLS
from agentx.infrastructure.database.qdrant.qdrant_vector_store import QdrantVectorStore


class MainDSPyReActAgent(dspy.Module):
    """Main ReAct agent for query processing.

    Uses DSPy ReAct pattern for multi-step reasoning with tools.
    Enhanced with QdrantVectorStore pre-retrieval for user history context.

    Phase 3 Fix: Now uses sync forward() for DSPy compatibility.
    """

    def __init__(self) -> None:
        """Initialize the main ReAct agent with tools and vector store."""
        super().__init__()
        self.vector_store = QdrantVectorStore()
        self.react = dspy.ReAct(
            signature=MainAgentSignature,
            tools=AVAILABLE_TOOLS,  # type: ignore[arg-type]
            max_iters=5,
        )

    def forward(
        self, query: str, user_id: str = "default", **kwargs
    ) -> dspy.Prediction:
        """Process a user query with user history context.

        Phase 3 Fix: Converted from async to sync for DSPy compatibility.
        DSPy does not support async forward() methods.

        Args:
            query: User's query
            user_id: User ID for history lookup (default: "default")
            **kwargs: Additional keyword arguments

        Returns:
            dspy.Prediction: Agent response with reasoning.
        """
        # Pre-retrieve user history from QdrantVectorStore (ColBERTv2)
        user_context = ""
        try:
            # Run async search_memories in event loop
            memories = asyncio.run(
                self.vector_store.search_memories(
                    query=query,  # FIX: Use actual user query
                    user_id=user_id,
                    limit=3,
                )
            )
            if memories:
                user_context = "\n".join([m.get("content", "") for m in memories])
        except Exception:
            # Continue without history if retrieval fails
            user_context = ""

        # Combine existing context with user history
        existing_context = kwargs.get("context", "")
        enhanced_context = f"{user_context}\n{existing_context}".strip()

        return self.react(query=query, context=enhanced_context, **kwargs)  # type: ignore[bad-return]


__all__ = ["MainDSPyReActAgent"]
