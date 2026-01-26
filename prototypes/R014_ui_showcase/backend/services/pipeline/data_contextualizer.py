# =============================================================================
# AGENTX DATA CONTEXTUALIZER Agent
# =============================================================================
# Phase 3: Rerank, Filter, Contextualize
# =============================================================================

import logging

import dspy
from services.pipeline.contextualizer_tracking_input import (
    track_input_data,
)
from services.pipeline.contextualizer_tracking_output import (
    track_build_return,
)
from services.pipeline.data_contextualizer_builder import (
    build_contextualized_return,
)
from services.pipeline.data_contextualizer_steps import (
    execute_contextualize_step,
    execute_filter_step,
    execute_rerank_step,
)
from services.tools.contextualizer import (
    ContextualizerModule,
    FilterModule,
    RerankerModule,
)

logger = logging.getLogger(__name__)


class DataContextualizerAgent(dspy.Module):
    """DATA CONTEXTUALIZER Agent: Reranks, filters, and contextualizes data.

    Takes research output and adds query context, removes noise,
    reranks by relevance for the specific query.
    """

    def __init__(self):
        super().__init__()
        # Tools for contextualization
        self.reranker = RerankerModule()
        self.filter = FilterModule()
        self.contextualizer = ContextualizerModule()

    def forward(
        self,
        research_data: dict,
        original_query: str = "",
    ) -> dict:
        """Execute DATA CONTEXTUALIZER agent pipeline.

        Args:
            research_data: Research output from RESEARCHER agent
            original_query: Original user query for context

        Returns:
            Contextualized and reranked data
        """
        track_input_data(research_data)

        query = research_data.get("query", original_query)
        raw_data = research_data.get("raw_data", [])
        beautiful_data = research_data.get("beautiful_data", {})

        # Step 1: Rerank by relevance
        ranked_result, _ = execute_rerank_step(self.reranker, query, raw_data)

        # Step 2: Filter out noise
        filtered_result, _ = execute_filter_step(
            self.filter, query, ranked_result, raw_data
        )

        # Step 3: Add query context
        contextualized_result, top_facts, _ = execute_contextualize_step(
            self.contextualizer, query, filtered_result, original_query
        )

        contextualized_data_final = (
            contextualized_result.get("contextualized_data", [])
            if hasattr(contextualized_result, "get")
            else []
        )

        # Track final assembly
        track_build_return(
            beautiful_data,
            contextualized_data_final,
            top_facts,
            research_data,
        )

        return build_contextualized_return(
            ranked_result=ranked_result,
            filtered_result=filtered_result,
            contextualized_result=contextualized_result,
            beautiful_data=beautiful_data,
            contextualized_data_final=contextualized_data_final,
            top_facts=top_facts,
            research_data=research_data,
        )

    async def aforward(
        self,
        research_data: dict,
        original_query: str = "",
    ) -> dict:
        """Async execute DATA CONTEXTUALIZER agent pipeline with parallel processing.

        Delegates to async_contextualize_forward for implementation.
        """
        from services.pipeline.data_contextualizer_async import (
            async_contextualize_forward,
        )

        return await async_contextualize_forward(self, research_data, original_query)
