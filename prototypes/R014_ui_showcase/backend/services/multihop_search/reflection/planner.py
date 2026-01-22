# =============================================================================
# AGENTX Multi-Hop Search - Hop Planner
# =============================================================================
# SRP: Only plans the next search hop.
# Takes gap_description and outputs next_query + strategy.
# =============================================================================

from __future__ import annotations

import dspy

from services.multihop_search.signatures import GenerateNextQuery


class HopPlanner(dspy.Module):
    """SRP: Only plans the next search hop.

    Takes gap_description and outputs next_query + strategy.
    """

    def __init__(self) -> None:
        super().__init__()
        self.plan = dspy.ChainOfThought(GenerateNextQuery)

    def forward(
        self,
        question: str,
        gap_description: str,
        previous_queries: list[str],
    ) -> dspy.Prediction:
        """Generate next search query and strategy.

        Args:
            question: Original question
            gap_description: What information is still missing
            previous_queries: Search queries already tried

        Returns:
            Prediction with next_query and strategy
        """
        return self.plan(  # type: ignore[bad-return]
            question=question,
            gap_description=gap_description,
            previous_queries=previous_queries,
        )
