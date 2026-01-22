# =============================================================================
# AGENTX Multi-Hop Search - DSPy Agents
# =============================================================================
# Multi-hop search agent (Infrastructure layer - DSPy integration)
# =============================================================================

from __future__ import annotations

import logging
import time
from typing import Any, Callable

import dspy

from services.multihop_search.execution.hop_orchestrator import HopOrchestrator
from services.multihop_search.reflection import CompletenessAssessor, HopPlanner
from services.multihop_search.result_builder import build_search_result
from services.multihop_search.search_client import get_search_client
from services.multihop_search.signatures import SynthesizeFinalAnswer
from services.multihop_search.time_estimator import get_time_estimator

logger = logging.getLogger(__name__)


class MultiHopSearchAgent(dspy.Module):
    """Multi-hop search agent (Infrastructure: DSPy framework integration).

    Orchestrates domain logic through HopOrchestrator.
    """

    def __init__(
        self,
        max_hops: int = 5,
        docs_per_hop: int = 5,
        progress_callback: Callable[[Any], Any] | None = None,
        stop_threshold: float = 0.85,
    ) -> None:
        super().__init__()
        self.max_hops = max_hops
        self.progress_callback = progress_callback

        self.answer_with_sources = dspy.ChainOfThought(
            "question, context -> answer, sources_summary"
        )
        self.synthesize_final = dspy.ChainOfThought(SynthesizeFinalAnswer)

        self.assessor = CompletenessAssessor()
        self.planner = HopPlanner()

        self.search_client = get_search_client(base_url="http://192.168.1.4:8080")
        self.time_estimator = get_time_estimator()

        self._orchestrator = HopOrchestrator(
            answer_module=self.answer_with_sources,
            assessor=self.assessor,
            planner=self.planner,
            time_estimator=self.time_estimator,
            max_hops=max_hops,
            stop_threshold=stop_threshold,
            docs_per_hop=docs_per_hop,
            search_client=self.search_client,
            progress_callback=progress_callback,
        )

    async def forward(self, question: str) -> dspy.Prediction:
        """Execute multi-hop search with runtime reflection."""
        overall_start = time.time()

        (
            hop_answers,
            hop_contexts,
            hop_queries,
            hop_num,
        ) = await self._orchestrator.execute_hops(question)

        self._send_progress(hop_num, "Synthesizing final answer...", 0.95)

        final_result = self.synthesize_final(  # type: ignore[bad-return]
            question=question,
            all_hop_answers=hop_answers,
            all_context=hop_contexts,
        )

        self._send_progress(hop_num, "Search complete", 1.0)

        return build_search_result(
            final_result=final_result,
            hop_answers=hop_answers,
            hop_queries=hop_queries,
            hop_num=hop_num,
            total_elapsed=time.time() - overall_start,
        )

    def _send_progress(
        self,
        hop_number: int,
        message: str,
        progress: float,
    ) -> None:
        """Send progress update via callback."""
        if self.progress_callback is None:
            return

        from services.multihop_search.schemas import HopEvent

        try:
            self.progress_callback(
                HopEvent(
                    event_type="hop_progress" if progress < 1.0 else "search_complete",
                    hop_number=hop_number,
                    total_hops=self.max_hops,
                    message=message,
                    progress=progress,
                )
            )
        except Exception:
            pass
