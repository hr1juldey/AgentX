"""Quality Check Module for Presenter agent.

Ported from R014: services/tools/presenter/quality_check.py

Performs quality validation of presented findings.
Wraps dspy.Predict(QualityCheck) as a testable module.

Fraud #12 fix: Returns dspy.Prediction instead of dict.
"""

import dspy

from agentx.agent.dspy_signatures.pipeline.presenter import QualityCheck
from agentx.agent.tools.common.dspy_helpers import safe_extract
from agentx.agent.tools.common.type_utils import _to_float, _to_bool


class QualityCheckModule(dspy.Module):
    """Performs quality check on presented findings.

    Validates:
    - Quality score (0.0 to 1.0)
    - Approval status
    - Any issues found

    Fraud #12 fix: Returns dspy.Prediction instead of dict.
    """

    def __init__(self) -> None:
        """Initialize the quality check module."""
        super().__init__()
        self.qa_checker = dspy.Predict(QualityCheck)

    def forward(self, presentation: str, user_query: str) -> dspy.Prediction:
        """Perform quality check on presentation.

        Args:
            presentation: Generated presentation text
            user_query: Original user query

        Returns:
            dspy.Prediction with 'quality_score', 'approved', and 'issues' keys
        """
        result = self.qa_checker(
            presentation=presentation,
            query=user_query,
        )

        quality_score = _to_float(
            safe_extract(result, "quality_score", 0.5), default=0.5
        )
        issues = safe_extract(result, "issues", "")
        approved = _to_bool(safe_extract(result, "approved", True), default=True)

        return dspy.Prediction(
            quality_score=quality_score,
            approved=approved,
            issues=issues,
        )
