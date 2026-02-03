"""Decision signatures for memory-guided search planning.

Provides DSPy signatures and modules for retrieving user preferences
and search guidance from memory to enhance query planning.
"""

import dspy

from agentx.infrastructure.database.qdrant.qdrant_vector_store import QdrantVectorStore


class SearchGuidanceSignature(dspy.Signature):
    """Signature for retrieving search guidance from memory.

    Memory does NOT store facts/knowledge. Memory stores:
    - Decision patterns (what routing worked before)
    - User preferences (sources, depth, format)
    - Search strategies (terms that worked, what failed)

    The LLM synthesizes retrieved patterns into actionable guidance.
    """

    query = dspy.InputField(desc="User's query")
    retrieved_preferences = dspy.InputField(
        desc="Retrieved user preferences from memory (JSON string)",
        default="{}",
    )
    search_depth = dspy.OutputField(
        desc="Search depth: 'shallow', 'medium', or 'deep'",
    )
    prioritized_terms = dspy.OutputField(
        desc="Comma-separated search terms based on past success",
    )
    source_preferences = dspy.OutputField(
        desc="Preferred sources: 'academic', 'general', 'news', etc.",
    )
    answer_format = dspy.OutputField(
        desc="Answer format: 'concise', 'detailed', 'bullet_points', etc.",
    )
    reasoning = dspy.OutputField(
        desc="Why this guidance was chosen based on memory",
    )


class SearchGuidanceModule(dspy.Module):
    """Memory-guided search planning module.

    Retrieves user preferences from memory and synthesizes them into
    search guidance for the query planner.

    CRITICAL: This ENHANCES the QueryPlanner, does NOT replace it.
    The 0-to-N task pattern is PRESERVED.
    """

    def __init__(self) -> None:
        """Initialize the search guidance module."""
        super().__init__()
        self.synthesize = dspy.Predict(SearchGuidanceSignature)
        self.vector_store = QdrantVectorStore()

    async def forward(self, query: str, user_id: str = "default") -> dspy.Prediction:
        """Retrieve memory context and synthesize search guidance.

        Args:
            query: User's query
            user_id: User ID for memory lookup

        Returns:
            dspy.Prediction: Search guidance for query planning
        """
        # Retrieve user preferences from memory
        memories = await self.vector_store.search_memories(
            query="user preferences search patterns sources format",
            user_id=user_id,
            limit=5,
        )

        # Format retrieved preferences as JSON
        import json

        retrieved_preferences = {}
        if memories:
            # Extract preference patterns from memories
            preferences_list = []
            for mem in memories:
                content = mem.get("content", "")
                metadata = mem.get("metadata", {})
                if "preference" in metadata.get("memory_type", "").lower():
                    preferences_list.append({"content": content, "metadata": metadata})

            retrieved_preferences = {"patterns": preferences_list}

        preferences_json = json.dumps(retrieved_preferences)

        # Synthesize guidance using LLM
        result = self.synthesize(
            query=query,
            retrieved_preferences=preferences_json,
        )

        return dspy.Prediction(
            search_depth=result.search_depth,  # type: ignore[attr-defined]
            prioritized_terms=result.prioritized_terms,  # type: ignore[attr-defined]
            source_preferences=result.source_preferences,  # type: ignore[attr-defined]
            answer_format=result.answer_format,  # type: ignore[attr-defined]
            reasoning=result.reasoning,  # type: ignore[attr-defined]
        )


__all__ = ["SearchGuidanceSignature", "SearchGuidanceModule"]
