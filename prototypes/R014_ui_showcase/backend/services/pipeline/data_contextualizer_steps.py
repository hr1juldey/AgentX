# =============================================================================
# AGENTX DATA CONTEXTUALIZER Step Processors
# =============================================================================
# Individual step processing logic for contextualizer pipeline
# =============================================================================

"""Step processing logic for data contextualizer pipeline.

Extracts the three main steps (rerank, filter, contextualize) into
separate functions for better modularity.
"""

import logging
import time

from services.pipeline.contextualizer_logging import (
    log_contextualize_result,
    log_filter_result,
    log_rerank_result,
)
from services.pipeline.contextualizer_tracking_steps import (
    track_contextualize_step,
    track_filter_step,
    track_rerank_step,
)
from services.pipeline.data_contextualizer_utils import extract_top_facts

logger = logging.getLogger(__name__)


def execute_rerank_step(reranker, query: str, raw_data: list) -> tuple[dict, float]:
    """Execute the reranking step.

    Args:
        reranker: Reranker module instance
        query: Query string
        raw_data: Raw research data

    Returns:
        Tuple of (ranked_result, step_time)
    """
    step_start = time.time()
    logger.info(f"  [CONTEXTUALIZER] Reranking {len(raw_data)} documents...")
    ranked_result_raw = reranker(query=query, results=raw_data)
    ranked_result: dict = (
        ranked_result_raw if hasattr(ranked_result_raw, "get") else {}  # type: ignore[bad-assignment]
    )
    step_time = time.time() - step_start
    track_rerank_step(raw_data, ranked_result, step_time)
    log_rerank_result(ranked_result, raw_data, step_time)
    return ranked_result, step_time


def execute_filter_step(
    filter_module, query: str, ranked_result: dict, raw_data: list
) -> tuple[dict, float]:
    """Execute the filtering step.

    Args:
        filter_module: Filter module instance
        query: Query string
        ranked_result: Result from reranking step
        raw_data: Raw research data (fallback)

    Returns:
        Tuple of (filtered_result, step_time)
    """
    step_start = time.time()
    logger.info("  [CONTEXTUALIZER] Filtering noise...")
    filter_input = (
        ranked_result.get("ranked_data") or raw_data
        if hasattr(ranked_result, "get")
        else raw_data
    )
    filtered_result_raw = filter_module(query=query, results=filter_input)
    filtered_result: dict = (
        filtered_result_raw if hasattr(filtered_result_raw, "get") else {}  # type: ignore[bad-assignment]
    )
    step_time = time.time() - step_start
    track_filter_step(filter_input, filtered_result, step_time)
    log_filter_result(filtered_result, step_time)
    return filtered_result, step_time


def execute_contextualize_step(
    contextualizer,
    query: str,
    filtered_result: dict,
    original_query: str,
) -> tuple[dict, list, float]:
    """Execute the contextualization step.

    Args:
        contextualizer: Contextualizer module instance
        query: Query string
        filtered_result: Result from filtering step
        original_query: Original user query

    Returns:
        Tuple of (contextualized_result, top_facts, step_time)
    """
    step_start = time.time()
    logger.info("  [CONTEXTUALIZER] Adding query context...")
    contextualize_input = (
        filtered_result.get("filtered_data") or []
        if hasattr(filtered_result, "get")
        else []
    )
    contextualized_result_raw = contextualizer(
        query=query,
        filtered_data=contextualize_input,
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
    track_contextualize_step(
        contextualize_input,
        contextualized_result,
        top_facts,
        step_time,
    )
    log_contextualize_result(contextualized_result, top_facts, step_time)
    return contextualized_result, top_facts, step_time
