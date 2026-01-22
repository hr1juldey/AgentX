# =============================================================================
# AGENTX Multi-Hop Search - Hop Orchestrator
# =============================================================================
# Orchestrates the execution of multi-hop search loops
# =============================================================================

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import dspy

from services.multihop_search.execution.hop_assessment import HopAssessment
from services.multihop_search.execution.hop_loop import HopLoopExecutor
from services.multihop_search.execution.hop_planning import HopPlanning
from services.multihop_search.execution.hop_search import HopSearch

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class HopOrchestrator:
    """Orchestrates the execution of multi-hop search loops.

    Delegates to specialized modules for SRP compliance.
    """

    def __init__(
        self,
        answer_module: dspy.ChainOfThought,
        assessor: Any,
        planner: Any,
        time_estimator: Any,
        max_hops: int,
        stop_threshold: float,
        docs_per_hop: int,
        search_client: Any,
        progress_callback: Any,
    ) -> None:
        """Initialize hop orchestrator."""
        self.max_hops = max_hops

        # Specialized modules
        search = HopSearch(search_client, docs_per_hop, time_estimator)
        assessment = HopAssessment(assessor)
        planning = HopPlanning(planner, time_estimator, progress_callback, max_hops)

        # Loop executor combines all modules
        self.loop_executor = HopLoopExecutor(
            search=search,
            assessment=assessment,
            planning=planning,
            answer_module=answer_module,
            max_hops=max_hops,
            stop_threshold=stop_threshold,
            progress_callback=progress_callback,
        )

    async def execute_hops(
        self,
        question: str,
    ) -> tuple[list[str], list[str], list[str], int]:
        """Execute multi-hop search loops.

        Returns:
            Tuple of (hop_answers, hop_contexts, hop_queries, hop_num)
        """
        hop_answers: list[str] = []
        hop_contexts: list[str] = []
        hop_queries: list[str] = []

        hop_num = 0
        plan_result: dspy.Prediction | None = None

        while hop_num < self.max_hops:
            hop_num += 1

            # Execute single hop iteration
            (
                context,
                search_query,
                plan_result,
                should_stop,
            ) = await self.loop_executor.execute_hop_iteration(
                question=question,
                hop_num=hop_num,
                plan_result=plan_result,
                hop_answers=hop_answers,
                hop_contexts=hop_contexts,
                hop_queries=hop_queries,
            )

            if should_stop:
                break

        return hop_answers, hop_contexts, hop_queries, hop_num
