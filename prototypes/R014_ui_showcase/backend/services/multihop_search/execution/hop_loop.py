# =============================================================================
# AGENTX Multi-Hop Search - Hop Loop Executor
# =============================================================================
# Executes a single iteration of the multi-hop search loop
# =============================================================================

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import dspy

from services.multihop_search.execution.hop_helpers import generate_hop_answer
from services.multihop_search.execution.progress import HopProgressTracker

if TYPE_CHECKING:
    from services.multihop_search.execution.hop_assessment import HopAssessment
    from services.multihop_search.execution.hop_planning import HopPlanning
    from services.multihop_search.execution.hop_search import HopSearch

logger = logging.getLogger(__name__)


class HopLoopExecutor:
    """Executes a single iteration of the multi-hop search loop.

    SRP: Execute one hop iteration only.
    """

    def __init__(
        self,
        search: "HopSearch",
        assessment: "HopAssessment",
        planning: "HopPlanning",
        answer_module: dspy.ChainOfThought,
        max_hops: int,
        stop_threshold: float,
        progress_callback: Any,
    ) -> None:
        """Initialize hop loop executor.

        Args:
            search: Hop search module
            assessment: Hop assessment module
            planning: Hop planning module
            answer_module: Answer generation module
            max_hops: Maximum number of hops
            stop_threshold: Threshold for stopping
            progress_callback: Progress callback
        """
        self.search = search
        self.assessment = assessment
        self.planning = planning
        self.answer_module = answer_module
        self.max_hops = max_hops
        self.stop_threshold = stop_threshold
        self.progress_tracker = HopProgressTracker(progress_callback, max_hops)

    async def execute_hop_iteration(
        self,
        question: str,
        hop_num: int,
        plan_result: dspy.Prediction | None,
        hop_answers: list[str],
        hop_contexts: list[str],
        hop_queries: list[str],
    ) -> tuple[str, str, dspy.Prediction | None, bool]:
        """Execute a single hop iteration.

        Args:
            question: Original question
            hop_num: Current hop number
            plan_result: Current plan result
            hop_answers: List of hop answers so far
            hop_contexts: List of hop contexts so far
            hop_queries: List of hop queries so far

        Returns:
            Tuple of (context, search_query, new_plan_result, should_stop)
        """
        # Generate search query
        search_query, strategy = self.search.generate_query(
            question, hop_num, plan_result
        )
        hop_queries.append(search_query)

        self.progress_tracker.send_hop_start(hop_num, strategy, search_query)

        # Execute search
        context, results, _ = await self.search.execute(search_query, strategy)
        hop_contexts.append(context)

        self.progress_tracker.send_documents_found(hop_num, len(results))  # type: ignore[arg-type]

        # Generate answer using helper
        answer = generate_hop_answer(self.answer_module, question, context)
        hop_answers.append(answer)

        # Assess completeness
        self.progress_tracker.send_assessing(hop_num)

        should_stop, reasoning, assessment = await self.assessment.assess(
            question=question,
            hop_answers=hop_answers,
            results=results,  # type: ignore[arg-type]
            stop_threshold=self.stop_threshold,
        )

        if should_stop:
            self.progress_tracker.send_complete(hop_num, reasoning)
            return context, search_query, plan_result, True

        # Plan next hop
        new_plan_result = await self.planning.plan_next(
            question=question,
            assessment=assessment,
            hop_queries=hop_queries,
            hop_num=hop_num,
        )

        return context, search_query, new_plan_result, False
