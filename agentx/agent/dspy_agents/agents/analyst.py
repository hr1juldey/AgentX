"""Analyst agent for query understanding.

Extracts intent and entities from user queries.
Enhanced with QdrantVectorStore pre-retrieval for user context.
"""

import dspy

from agentx.agent.dspy_signatures.main_signatures import AnalystSignature
from agentx.infrastructure.database.qdrant.qdrant_vector_store import QdrantVectorStore


class AnalystAgent(dspy.Module):
    """Analyst agent for query understanding and intent extraction.

    Enhanced with QdrantVectorStore pre-retrieval for user context.
    """

    def __init__(self) -> None:
        """Initialize the analyst agent with vector store."""
        super().__init__()
        self.vector_store = QdrantVectorStore()
        self.analyze = dspy.Predict(AnalystSignature)

    async def forward(self, query: str, user_id: str = "default") -> dspy.Prediction:
        """Analyze user query to extract intent and entities.

        Args:
            query: User's question or request.
            user_id: User ID for context lookup (default: "default").

        Returns:
            dspy.Prediction: Analysis results with intent, entities, tool needs.
        """
        # Pre-retrieve user context from QdrantVectorStore (ColBERTv2)
        user_context = ""
        try:
            memories = await self.vector_store.search_memories(
                query="user query patterns intent extraction history",
                user_id=user_id,
                limit=3,
            )
            if memories:
                user_context = "\n".join([m.get("content", "") for m in memories])
        except Exception:
            # Continue without context if retrieval fails
            user_context = ""

        # Build enhanced query with user context
        enhanced_query = query
        if user_context:
            enhanced_query = f"{query}\n[User Context: {user_context}]"

        result = self.analyze(query=enhanced_query)
        return dspy.Prediction(
            intent=result.intent,  # type: ignore[attr-defined]
            entities=result.entities,  # type: ignore[attr-defined]
            tool_needed=result.tool_needed,  # type: ignore[attr-defined]
            tool_name=result.tool_name,  # type: ignore[attr-defined]
        )
