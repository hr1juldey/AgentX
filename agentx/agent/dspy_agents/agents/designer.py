"""Designer agent for UI widget selection.

Server-driven UI pattern - selects widgets with state awareness.
Enhanced with QdrantVectorStore pre-retrieval for UI preferences.
"""

import dspy

from agentx.agent.dspy_signatures.main_signatures import DesignerSignature
from agentx.infrastructure.database.qdrant.qdrant_vector_store import QdrantVectorStore


class DesignerAgent(dspy.Module):
    """Designer agent for UI widget selection.

    Server-driven UI pattern from C007.
    Enhanced with QdrantVectorStore pre-retrieval for UI preferences.
    """

    def __init__(self) -> None:
        """Initialize the designer agent with vector store."""
        super().__init__()
        self.vector_store = QdrantVectorStore()
        self.design = dspy.Predict(DesignerSignature)

    async def forward(
        self,
        query: str,
        response: str,
        existing_widgets: list[str],
        user_id: str = "default",
    ) -> dspy.Prediction:
        """Select appropriate UI widget based on query and context.

        Args:
            query: User's question or request.
            response: Agent's response content.
            existing_widgets: List of already shown widget types.
            user_id: User ID for preference lookup (default: "default").

        Returns:
            dspy.Prediction: Widget recommendation with type and props.
        """
        # Pre-retrieve UI preferences from QdrantVectorStore (ColBERTv2)
        ui_context = ""
        try:
            memories = await self.vector_store.search_memories(
                query="UI preferences widget choices design style format",
                user_id=user_id,
                limit=5,
            )
            if memories:
                ui_context = "\n".join([m.get("content", "") for m in memories])
        except Exception:
            # Continue without preferences if retrieval fails
            ui_context = ""

        # Build enhanced response with UI preferences
        enhanced_response = response
        if ui_context:
            enhanced_response = f"{response}\n[UI Preferences: {ui_context}]"

        result = self.design(
            query=query,
            response=enhanced_response,
            existing_widgets=existing_widgets,
        )
        return dspy.Prediction(
            recommended_widget=result.recommended_widget,  # type: ignore[attr-defined]
            widget_props=result.widget_props,  # type: ignore[attr-defined]
        )
