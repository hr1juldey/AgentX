"""Analyst Agent - differentiated stem cell for analysis tasks."""

import dspy

from agentx.application.agents.stem_cell import StemCellAgent


class AnalystAgent(StemCellAgent):
    """Analyst agent for query analysis and data judgment tasks.

    Differentiated via specialized signature:
    "query, memory_context, knowledge_context -> context_summary, goals, is_sufficient, confidence"
    """

    def __init__(self, user_id: str) -> None:
        """Initialize the analyst agent.

        Args:
            user_id: User identifier for memory isolation
        """
        # Create analyst-specific signature using standard DSPy pattern
        analyst_signature = dspy.Signature(  # type: ignore[call-arg]
            "query, memory_context, knowledge_context -> "
            "context_summary, goals, is_sufficient, confidence"
        )

        super().__init__(user_id=user_id, signature=analyst_signature)

        # Overexpression: Add specialized data judgment module
        self.data_judgment = dspy.ChainOfThought("query, data -> judgment")
