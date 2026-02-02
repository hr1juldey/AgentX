"""Analyst agent for query understanding.

Extracts intent and entities from user queries.
"""

import dspy

from agentx.agent.dspy_signatures.main_signatures import AnalystSignature


class AnalystAgent(dspy.Module):
    """Analyst agent for query understanding and intent extraction."""

    def __init__(self) -> None:
        """Initialize the analyst agent."""
        super().__init__()
        self.analyze = dspy.Predict(AnalystSignature)

    def forward(self, query: str) -> dspy.Prediction:
        """Analyze user query to extract intent and entities.

        Args:
            query: User's question or request.

        Returns:
            dspy.Prediction: Analysis results with intent, entities, tool needs.
        """
        result = self.analyze(query=query)
        return dspy.Prediction(
            intent=result.intent,  # type: ignore[attr-defined]
            entities=result.entities,  # type: ignore[attr-defined]
            tool_needed=result.tool_needed,  # type: ignore[attr-defined]
            tool_name=result.tool_name,  # type: ignore[attr-defined]
        )
