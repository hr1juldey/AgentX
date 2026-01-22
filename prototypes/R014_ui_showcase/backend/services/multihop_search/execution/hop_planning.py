# =============================================================================
# AGENTX Multi-Hop Search - Hop Planning Module
# =============================================================================
# Plans the next hop based on assessment results
# =============================================================================

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import dspy

if TYPE_CHECKING:
    from services.multihop_search.reflection import HopPlanner

logger = logging.getLogger(__name__)


class HopPlanning:
    """Plans the next hop based on assessment.

    SRP: Plan next hop only.
    """

    def __init__(
        self,
        planner: "HopPlanner",
        time_estimator: Any,
        progress_callback: Any,
        max_hops: int,
    ) -> None:
        """Initialize hop planning module.

        Args:
            planner: Hop planner module
            time_estimator: Time estimator service
            progress_callback: Progress callback function
            max_hops: Maximum hops for progress calculation
        """
        self.planner = planner
        self.time_estimator = time_estimator
        self.progress_callback = progress_callback
        self.max_hops = max_hops

    def _send_progress(
        self,
        event_type: str,
        hop_number: int,
        message: str,
        progress: float,
        eta_seconds: float | None = None,
        reflection_reasoning: str | None = None,
    ) -> None:
        """Send progress update via callback."""
        if self.progress_callback is None:
            return

        from services.multihop_search.execution.hop_helpers import send_progress_event

        send_progress_event(
            callback=self.progress_callback,
            event_type=event_type,
            hop_number=hop_number,
            total_hops=self.max_hops,
            message=message,
            progress=progress,
            eta_seconds=eta_seconds,
            reflection_reasoning=reflection_reasoning,
        )

    async def plan_next(
        self,
        question: str,
        assessment: dspy.Prediction,
        hop_queries: list[str],
        hop_num: int,
    ) -> dspy.Prediction:
        """Plan the next hop based on assessment.

        Args:
            question: User's question
            assessment: Assessment prediction from current hop
            hop_queries: Accumulated search queries
            hop_num: Current hop number

        Returns:
            Plan result with next_query and strategy
        """
        self._send_progress(
            event_type="hop_progress",
            hop_number=hop_num,
            message="Planning next hop...",
            progress=(hop_num - 0.2) / self.max_hops,
        )

        plan_result = self.planner(  # type: ignore[bad-assignment]
            question=question,
            gap_description=assessment.gap_description,  # type: ignore[missing-attribute]
            previous_queries=hop_queries,
        )

        # Build reasoning for progress update
        reasoning = (
            f"Gap: {assessment.gap_description[:100]}\n"  # type: ignore[missing-attribute]
            f"Strategy: {plan_result.strategy}\n"  # type: ignore[missing-attribute]
            f"Next: {plan_result.next_query}"  # type: ignore[missing-attribute]
        )

        plan_strategy = plan_result.strategy  # type: ignore[missing-attribute]
        eta = self.time_estimator.estimate_total_time(1, [plan_strategy])

        self._send_progress(
            event_type="hop_complete",
            hop_number=hop_num,
            message=f"Continuing: {plan_strategy}",  # type: ignore[missing-attribute]
            progress=hop_num / self.max_hops,
            eta_seconds=eta,
            reflection_reasoning=reasoning,
        )

        logger.info(
            f"Hop {hop_num}: strategy={plan_result.strategy}"  # type: ignore[missing-attribute]
        )

        return plan_result
