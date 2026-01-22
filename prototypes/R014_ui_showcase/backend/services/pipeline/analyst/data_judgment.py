# =============================================================================
# AGENTX ANALYST - Data Judgment
# =============================================================================
# Pass 2: Data quality and completeness judgment
# =============================================================================

from typing import Any, Dict

from services.tools.analyst import DataQualityCheckerModule


class DataJudgmentHandler:
    """Handles Pass 2: Data quality and completeness judgment."""

    def __init__(self, data_quality_checker: DataQualityCheckerModule):
        """Initialize data judgment handler.

        Args:
            data_quality_checker: Data quality checker module
        """
        self.data_quality_checker = data_quality_checker

    def judge(self, user_query: str, contextualized_data: dict) -> Dict[str, Any]:
        """Judge data quality and completeness.

        Args:
            user_query: The user's query
            contextualized_data: Data from contextualizer

        Returns:
            Judgment result dict
        """
        judgment_result = self.data_quality_checker(
            query=user_query,
            data=contextualized_data.get("contextualized_data", contextualized_data),
        )
        judgment = judgment_result if hasattr(judgment_result, "get") else {}

        return {
            "data_quality": judgment.get("data_quality", "medium")
            if hasattr(judgment, "get")
            else "medium",
            "data_completeness": judgment.get("data_completeness", 0.5)
            if hasattr(judgment, "get")
            else 0.5,
            "query_relevance": judgment.get("query_relevance", "medium")
            if hasattr(judgment, "get")
            else "medium",
            "needs_more_research": judgment.get("needs_more_research", False)
            if hasattr(judgment, "get")
            else False,
            "judgment": judgment.get("reason", "") if hasattr(judgment, "get") else "",
        }
