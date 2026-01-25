# =============================================================================
# AGENTX Contextualizer - Step Data Tracking
# =============================================================================
# Tracks data flow through each contextualizer step
# =============================================================================

import logging

logger = logging.getLogger(__name__)


def track_rerank_step(raw_data: list, ranked_result: dict, step_time: float) -> None:
    """Track rerank step with input/output comparison.

    Shows input count, output count, scores, avg relevance.
    """
    logger.info("      [RERANK STEP] Data flow:")

    input_count = len(raw_data)
    ranked_data = ranked_result.get("ranked_data", [])
    scores = ranked_result.get("scores", [])
    avg_score = sum(scores) / len(scores) if scores else 0

    logger.info(f"        - Input: {input_count} documents")
    logger.info(f"        - Output: {len(ranked_data)} documents")
    logger.info(f"        - Scores: {len(scores)} scores, avg={avg_score:.2f}")

    if ranked_data:
        sample = ranked_data[0]
        title = sample.get("title", sample.get("url", ""))[:50]
        logger.info(f"        - Top result: '{title}...'")


def track_filter_step(
    ranked_data: list, filtered_result: dict, step_time: float
) -> None:
    """Track filter step with input/output comparison.

    Shows input count, output count, removed count.
    Warns if high removal rate detected.
    """
    logger.info("      [FILTER STEP] Data flow:")

    input_count = len(ranked_data)
    filtered_data = filtered_result.get("filtered_data", [])
    removed_count = filtered_result.get("removed_count", 0)

    logger.info(f"        - Input: {input_count} documents")
    logger.info(f"        - Output: {len(filtered_data)} documents")
    logger.info(f"        - Removed: {removed_count} items")

    if removed_count > input_count * 0.5:
        logger.warning(
            f"        - ⚠️  High removal rate: {removed_count}/{input_count} ({removed_count / input_count:.0%})"
        )


def track_contextualize_step(
    filtered_data: list,
    contextualized_result: dict,
    top_facts: list,
    step_time: float,
) -> None:
    """Track contextualize step with input/output comparison.

    Shows input count, output count, extracted facts count.
    """
    logger.info("      [CONTEXTUALIZE STEP] Data flow:")

    input_count = len(filtered_data)
    contextualized_data = contextualized_result.get("contextualized_data", [])

    logger.info(f"        - Input: {input_count} documents")
    logger.info(f"        - Output: {len(contextualized_data)} documents")
    logger.info(f"        - Extracted: {len(top_facts)} top_facts")

    if top_facts:
        sample_facts = top_facts[:2]
        for i, fact in enumerate(sample_facts, 1):
            fact_str = str(fact)[:60]
            logger.info(f"        - Fact {i}: '{fact_str}...'")
