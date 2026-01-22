# =============================================================================
# AGENTX Analyst - Data Quality Checker Module
# =============================================================================
# Assesses data quality and completeness
# =============================================================================

import dspy

from services.tools.analyst.signatures import (
    AssessCompletenessSignature,
    AssessRelevanceSignature,
    DecideResearchSignature,
)
from services.tools.common.type_utils import _to_bool, _to_float


class DataQualityCheckerModule(dspy.Module):
    """Assesses data quality and completeness (for ANALYST Pass 2).

    Has 3 signatures:
    - AssessCompleteness: Assess if data is complete (returns float)
    - AssessRelevance: Assess if data is relevant to query (returns float)
    - DecideResearch: Decide if more research is needed (uses float inputs)
    """

    def __init__(self):
        super().__init__()
        # Use class-based signatures with float type annotations
        self.assess_completeness = dspy.Predict(AssessCompletenessSignature)
        self.assess_relevance = dspy.Predict(AssessRelevanceSignature)
        self.decide_research = dspy.Predict(DecideResearchSignature)

    def forward(self, query: str, data: dict) -> dict:
        """Assess data quality."""
        completeness_result = self.assess_completeness(query=query, data=str(data))
        relevance_result = self.assess_relevance(query=query, data=str(data))

        # Safely convert scores to float (handles text values like "High")
        completeness_score = _to_float(
            completeness_result.completeness_score  # type: ignore[attr-defined]
        )
        relevance_score = _to_float(
            relevance_result.relevance_score  # type: ignore[attr-defined]
        )

        decision_result = self.decide_research(
            completeness_score=completeness_score,
            relevance_score=relevance_score,
        )

        # Safely convert bool
        needs_more_research = _to_bool(
            decision_result.needs_more_research,  # type: ignore[attr-defined]
            default=(completeness_score < 0.7),
        )

        return {
            "data_quality": "high" if completeness_score > 0.7 else "low",
            "data_completeness": completeness_score,
            "query_relevance": relevance_score,
            "needs_more_research": needs_more_research,
            "reason": decision_result.reason,  # type: ignore[attr-defined]
        }
