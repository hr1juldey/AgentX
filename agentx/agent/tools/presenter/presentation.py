"""Presentation Module for Presenter agent.

Ported from R014: services/tools/presenter/presentation.py

Presents findings in polished format.
Wraps dspy.Predict(PresentFindings) as a testable module.

Fraud #13 fix: Returns dspy.Prediction instead of dict.
"""

import dspy

from agentx.agent.dspy_signatures.pipeline.presenter import PresentFindings
from agentx.agent.tools.common.dspy_helpers import safe_extract


class PresentationModule(dspy.Module):
    """Presents findings in polished format.

    Wraps the PresentFindings signature for consistent module interface.

    Fraud #13 fix: Returns dspy.Prediction instead of dict.
    """

    def __init__(self) -> None:
        """Initialize the presentation module."""
        super().__init__()
        self.presenter = dspy.Predict(PresentFindings)

    def forward(self, findings: str, user_query: str) -> dspy.Prediction:
        """Generate polished presentation.

        Args:
            findings: Research findings to present
            user_query: Original user query

        Returns:
            dspy.Prediction with 'presentation' key
        """
        result = self.presenter(
            raw_findings=findings,
            query=user_query,
        )

        presentation = safe_extract(result, "presentation", "")

        return dspy.Prediction(
            presentation=presentation,
        )
