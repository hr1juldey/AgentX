"""Context Analyzer Module for Analyst agent.

Ported from R014: services/tools/analyst/query_analyzer.py

Analyzes the context and domain of the user query using 3 parallel Predict calls.
"""

import dspy

from agentx.agent.tools.common.dspy_helpers import safe_extract


class ContextAnalyzerModule(dspy.Module):
    """Analyzes the context and domain of the user query.

    Uses 3 parallel Predict calls to analyze:
    - Query type (question, task, comparison, analysis, or other)
    - Subject domain (economics, technology, science, general, etc.)
    - Urgency level (immediate, routine, or background)
    """

    def __init__(self) -> None:
        """Initialize the context analyzer."""
        super().__init__()
        self.detect_type = dspy.Predict("query -> query_type")
        self.extract_domain = dspy.Predict("query -> domain")
        self.identify_urgency = dspy.Predict("query -> urgency")

    def forward(self, query: str) -> dict:
        """Analyze query context.

        Args:
            query: User's question or request

        Returns:
            dict with 'query_type', 'domain', and 'urgency'
        """
        type_result = self.detect_type(query=query)
        domain_result = self.extract_domain(query=query)
        urgency_result = self.identify_urgency(query=query)

        return {
            "query_type": safe_extract(type_result, "query_type", "unknown"),
            "domain": safe_extract(domain_result, "domain", "general"),
            "urgency": safe_extract(urgency_result, "urgency", "routine"),
        }
