# =============================================================================
# AGENTX Multi-Hop Search - Completeness Assessor
# =============================================================================
# SRP: Only assesses whether current information is sufficient.
# Does NOT plan next hops - that's HopPlanner's job.
# =============================================================================

from __future__ import annotations

import dspy

from services.multihop_search.signatures import CheckCompleteness


class CompletenessAssessor(dspy.Module):
    """SRP: Only assesses whether current information is sufficient.

    Does NOT plan next hops - that's HopPlanner's job.
    """

    def __init__(self) -> None:
        super().__init__()
        self.check = dspy.ChainOfThought(CheckCompleteness)

    def forward(
        self,
        question: str,
        current_answer: str,
        documents_summary: str,
    ) -> dspy.Prediction:
        """Check if we have enough information.

        Args:
            question: Original question
            current_answer: Current best answer from all hops
            documents_summary: Brief summary of documents found

        Returns:
            Prediction with is_sufficient, confidence, gap_description
        """
        return self.check(  # type: ignore[bad-return]
            question=question,
            current_answer=current_answer,
            documents_summary=documents_summary,
        )
