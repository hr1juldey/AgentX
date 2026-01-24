# =============================================================================
# AGENTX CONTEXTUALIZER Logging Utilities
# =============================================================================
# Helper functions for contextualizer logging
# =============================================================================

from services.pipeline.agent_logging import log_step_result, safe_get, safe_get_list


def extract_rerank_metrics(ranked_result: dict, raw_data: list) -> dict:
    """Extract rerank metrics from result.

    Args:
        ranked_result: Result from reranker
        raw_data: Original raw data list

    Returns:
        Dictionary with rerank metrics
    """
    ranked_data = safe_get(ranked_result, "ranked_data", raw_data)
    relevance_scores = safe_get_list(ranked_result, "scores")
    avg_score = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0
    return {
        "Reranked": f"{len(ranked_data)} documents",
        "avg score": f"{avg_score:.2f}",
    }


def extract_filter_metrics(filtered_result: dict) -> dict:
    """Extract filter metrics from result.

    Args:
        filtered_result: Result from filter

    Returns:
        Dictionary with filter metrics
    """
    filtered_data = safe_get_list(filtered_result, "filtered_data")
    removed_count = safe_get(filtered_result, "removed_count", 0)
    return {
        "Filtered": f"{len(filtered_data)} kept",
        "removed": removed_count,
    }


def extract_contextualize_metrics(contextualized_result: dict, top_facts: list) -> dict:
    """Extract contextualize metrics from result.

    Args:
        contextualized_result: Result from contextualizer
        top_facts: Extracted top facts

    Returns:
        Dictionary with contextualize metrics
    """
    contextualized_data = safe_get_list(contextualized_result, "contextualized_data")
    return {
        "Extracted": f"{len(top_facts)} key facts",
        "from": f"{len(contextualized_data)} documents",
    }


def log_rerank_result(ranked_result: dict, raw_data: list, step_time: float) -> None:
    """Log rerank results.

    Args:
        ranked_result: Result from reranker
        raw_data: Original raw data list
        step_time: Time taken for this step
    """
    metrics = extract_rerank_metrics(ranked_result, raw_data)
    log_step_result("Reranked", metrics, step_time)


def log_filter_result(filtered_result: dict, step_time: float) -> None:
    """Log filter results.

    Args:
        filtered_result: Result from filter
        step_time: Time taken for this step
    """
    metrics = extract_filter_metrics(filtered_result)
    log_step_result("Filtered", metrics, step_time)


def log_contextualize_result(
    contextualized_result: dict, top_facts: list, step_time: float
) -> None:
    """Log contextualize results.

    Args:
        contextualized_result: Result from contextualizer
        top_facts: Extracted top facts
        step_time: Time taken for this step
    """
    metrics = extract_contextualize_metrics(contextualized_result, top_facts)
    log_step_result("Extracted", metrics, step_time)
