"""Data Quality Checker Module for Analyst agent.

Ported from R014: services/tools/analyst/signatures.py

Assesses the quality and completeness of research data (Pass 2).
Used in the second pass of the Analyst agent to judge if more research is needed.
"""

import dspy

from agentx.agent.dspy_signatures.analyst import AssessDataQuality
from agentx.agent.tools.common.type_utils import _to_bool, _to_float
from agentx.agent.tools.common.dspy_helpers import safe_extract


class DataQualityCheckerModule(dspy.Module):
    """Assesses the quality and completeness of research data (Pass 2).

    Evaluates whether the research data is sufficient to answer the user query
    or if more research is needed.
    """

    def __init__(self) -> None:
        """Initialize the data quality checker."""
        super().__init__()
        self.assessor = dspy.ChainOfThought(AssessDataQuality)

    def forward(self, query: str, data: dict) -> dict:
        """Assess data quality and completeness.

        Args:
            query: Original user query
            data: Research data to assess (from contextualizer)

        Returns:
            dict with completeness_score, relevance_score, missing_elements, needs_more_research
        """
        result = self.assessor(query=query, data=str(data))

        return {
            "completeness_score": _to_float(
                safe_extract(result, "completeness_score", 0.5), default=0.5
            ),
            "relevance_score": _to_float(
                safe_extract(result, "relevance_score", 0.5), default=0.5
            ),
            "missing_elements": safe_extract(result, "missing_elements", ""),
            "needs_more_research": _to_bool(
                safe_extract(result, "needs_more_research", False), default=False
            ),
        }
