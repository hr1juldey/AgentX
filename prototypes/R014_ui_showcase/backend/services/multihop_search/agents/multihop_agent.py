# =============================================================================
# AGENTX Multi-Hop Search - Main Agent
# =============================================================================
# Multi-hop search agent with hardware-adaptive async execution
# =============================================================================

from __future__ import annotations

import logging
from typing import Any, Callable

import dspy

from services.multihop_search.agents.async_execution import AsyncExecutionMixin
from services.multihop_search.agents.async_forward import AsyncForwardMixin
from services.multihop_search.agents.sync_forward import SyncForwardMixin
from services.multihop_search.execution.hop_orchestrator import HopOrchestrator
from services.multihop_search.reflection import CompletenessAssessor, HopPlanner
from services.multihop_search.search_client import get_search_client
from services.multihop_search.signatures import SynthesizeFinalAnswer
from services.multihop_search.time_estimator import get_time_estimator

logger = logging.getLogger(__name__)


class MultiHopSearchAgent(
    dspy.Module,
    AsyncExecutionMixin,
    SyncForwardMixin,
    AsyncForwardMixin,
):
    """Multi-hop search agent with hardware-adaptive async execution.

    Automatically detects GPU capabilities and uses optimal execution strategy:
    - RTX 3060: Sequential execution
    - DGX Pro: Parallel I/O operations

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
        self.executor = self._init_executor("MultiHopSearchAgent")

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
