"""Context Analyzer Module for Analyst agent.

Ported from R014: services/tools/analyst/query_analyzer.py

Analyzes the context and domain of the user query using AnalyzeQueryContext.

Fraud #6 fix: Returns dspy.Prediction instead of dict.
"""

import dspy

from agentx.agent.dspy_signatures.analyst import AnalyzeQueryContext
from agentx.agent.tools.common.dspy_helpers import safe_extract


class ContextAnalyzerModule(dspy.Module):
    """Analyzes the context and domain of the user query.

    Uses AnalyzeQueryContext signature to analyze:
    - Query type (question, task, comparison, analysis, or other)
    - Subject domain (economics, technology, science, general, etc.)
    - Urgency level (immediate, routine, or background)

    Fraud #6 fix: Returns dspy.Prediction instead of dict.
    """

    def __init__(self) -> None:
        """Initialize the context analyzer."""
        super().__init__()
        self.analyzer = dspy.Predict(AnalyzeQueryContext)

    def forward(self, query: str) -> dspy.Prediction:
        """Analyze query context.

        Args:
            query: User's question or request

        Returns:
            dspy.Prediction with 'query_type', 'domain', and 'urgency'
        """
        result = self.analyzer(query=query)

        return dspy.Prediction(
            query_type=safe_extract(result, "query_type", "unknown"),
            domain=safe_extract(result, "domain", "general"),
            urgency=safe_extract(result, "urgency", "routine"),
        )
