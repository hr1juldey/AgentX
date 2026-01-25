# =============================================================================
# AGENTX DATA CONTEXTUALIZER - Async Implementation
# =============================================================================
# Async parallel processing for contextualizer pipeline
# =============================================================================

import logging
import time

from services.pipeline.contextualizer_logging import (
    log_contextualize_result,
    log_filter_result,
    log_rerank_result,
)
from services.pipeline.data_contextualizer_builder import (
    build_contextualized_return,
)
from services.pipeline.data_contextualizer_utils import extract_top_facts

logger = logging.getLogger(__name__)


async def async_contextualize_forward(
    agent, research_data: dict, original_query: str = ""
) -> dict:
    """Async execute DATA CONTEXTUALIZER agent pipeline with parallel processing.

    Uses async for reranking, filtering, and contextualization steps to achieve
    ~4x speedup with 4 concurrent LLM calls per step.

    Args:
        agent: DataContextualizerAgent instance with reranker/filter/contextualizer
        research_data: Research output from RESEARCHER agent
        original_query: Original user query for context

    Returns:
        Contextualized and reranked data
    """
    query = research_data.get("query", original_query)
    raw_data = research_data.get("raw_data", [])
    beautiful_data = research_data.get("beautiful_data", {})

    # Step 1: Async rerank by relevance
    step_start = time.time()
    logger.info(f"  [CONTEXTUALIZER] Reranking {len(raw_data)} documents (async)...")
    ranked_result_raw = await agent.reranker.aforward(query=query, results=raw_data)
    ranked_result: dict = (
        ranked_result_raw if hasattr(ranked_result_raw, "get") else {}  # type: ignore[bad-assignment]
    )
    step_time = time.time() - step_start
    log_rerank_result(ranked_result, raw_data, step_time)

    # Step 2: Async filter out noise
    step_start = time.time()
    logger.info("  [CONTEXTUALIZER] Filtering noise (async)...")
    filtered_result_raw = await agent.filter.aforward(
        query=query,
        results=ranked_result.get("ranked_data", raw_data)
        if hasattr(ranked_result, "get")
        else raw_data,
    )
    filtered_result: dict = (
        filtered_result_raw if hasattr(filtered_result_raw, "get") else {}  # type: ignore[bad-assignment]
    )
    step_time = time.time() - step_start
    log_filter_result(filtered_result, step_time)

    # Step 3: Async add query context
    step_start = time.time()
    logger.info("  [CONTEXTUALIZER] Adding query context (async)...")
    contextualized_result_raw = await agent.contextualizer.aforward(
        query=query,
        filtered_data=filtered_result.get("filtered_data", [])
        if hasattr(filtered_result, "get")
        else [],
        original_query=original_query,
    )
    contextualized_result: dict = (
        contextualized_result_raw  # type: ignore[bad-assignment]
        if hasattr(contextualized_result_raw, "get")
        else {}
    )

    contextualized_data_final = (
        contextualized_result.get("contextualized_data", [])
        if hasattr(contextualized_result, "get")
        else []
    )
    top_facts = extract_top_facts(contextualized_data_final)
    step_time = time.time() - step_start
    log_contextualize_result(contextualized_result, top_facts, step_time)

    return build_contextualized_return(
        ranked_result=ranked_result,
        filtered_result=filtered_result,
        contextualized_result=contextualized_result,
        beautiful_data=beautiful_data,
        contextualized_data_final=contextualized_data_final,
        top_facts=top_facts,
        research_data=research_data,
    )
