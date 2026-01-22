# =============================================================================
# AGENTX Multi-Hop Search - Hop Assessment Module
# =============================================================================
# Assesses completeness of hop results and determines if search should continue
# =============================================================================

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import dspy

from services.multihop_search.execution.hop_helpers import summarize_documents
from services.multihop_search.search_client import SearchResultItem

if TYPE_CHECKING:
    from services.multihop_search.reflection import CompletenessAssessor

logger = logging.getLogger(__name__)


class HopAssessment:
    """Assesses completeness of hop results.

    SRP: Assess completeness and determine if stopping is appropriate.
    """

    def __init__(
        self,
        assessor: "CompletenessAssessor",
    ) -> None:
        """Initialize hop assessment module.

        Args:
            assessor: Completeness assessor module
        """
        self.assessor = assessor

    async def assess(
        self,
        question: str,
        hop_answers: list[str],
        results: list[SearchResultItem],
        stop_threshold: float,
    ) -> tuple[bool, str, dspy.Prediction]:
        """Assess if we have enough information to answer.

        Args:
            question: User's question
            hop_answers: Accumulated hop answers
            results: Search results from this hop
            stop_threshold: Confidence threshold for stopping

        Returns:
            Tuple of (should_stop, reasoning, assessment)
        """
        current_answer = "\n\n".join(hop_answers)
        documents_summary = summarize_documents(results)

        assessment = self.assessor(  # type: ignore[bad-return]
            question=question,
            current_answer=current_answer,
            documents_summary=documents_summary,
        )

        # Check stop conditions
        is_sufficient_val = assessment.is_sufficient  # type: ignore[missing-attribute]
        confidence_val = assessment.confidence  # type: ignore[missing-attribute]

        if is_sufficient_val or confidence_val >= stop_threshold:
            reasoning = f"Complete (confidence: {confidence_val:.0%})"
            logger.info(f"Stopping: sufficient info at {confidence_val:.0%}")
            return True, reasoning, assessment

        # Need more info
        gap_desc = assessment.gap_description  # type: ignore[missing-attribute]
        reasoning = f"Insufficient: {gap_desc[:100]}..."
        return False, reasoning, assessment

    def get_gap_description(self, assessment: dspy.Prediction) -> str:
        """Extract gap description from assessment.

        Args:
            assessment: Assessment prediction

        Returns:
            Gap description string
        """
        return assessment.gap_description  # type: ignore[missing-attribute]

    def get_confidence(self, assessment: dspy.Prediction) -> float:
        """Extract confidence from assessment.

        Args:
            assessment: Assessment prediction

        Returns:
            Confidence value
        """
        return assessment.confidence  # type: ignore[missing-attribute]
