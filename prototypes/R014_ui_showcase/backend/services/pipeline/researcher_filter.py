# =============================================================================
# AGENTX Researcher Result Filtering
# =============================================================================
# Score-based filtering with logging to reduce contextualizer load
# =============================================================================

import logging

logger = logging.getLogger(__name__)


# Constants (Rule 5: No magic numbers)
MAX_RESULTS = 25
SCORE_LOG_SAMPLE_SIZE = 5
DISCARD_SAMPLE_SIZE = 5


def filter_and_log_results(
    sorted_results: list, source_description: str = "results"
) -> list:
    """Filter results by score with comprehensive logging.

    Args:
        sorted_results: Results sorted by SearXNG score (descending)
        source_description: Description of result source for logs

    Returns:
        Filtered results capped at MAX_RESULTS
    """
    if not sorted_results:
        logger.info(f"[RESEARCHER] No {source_description} to filter")
        return sorted_results

    # Log score distribution for debugging
    scores = [r.get("score", 0) for r in sorted_results]
    logger.info(
        f"[RESEARCHER] Score distribution: min={min(scores):.3f}, "
        f"max={max(scores):.3f}, avg={sum(scores) / len(scores):.3f}"
    )

    # Log top results
    top_results = [
        (i + 1, r.get("title", "")[:50], r.get("score", 0))
        for i, r in enumerate(sorted_results[:SCORE_LOG_SAMPLE_SIZE])
    ]
    logger.info(f"[RESEARCHER] Top {len(top_results)} {source_description} by score:")
    for rank, title, score in top_results:
        logger.info(f"    [{rank}] {title}... (score: {score:.3f})")

    # Cap at MAX_RESULTS to balance quality vs processing time
    # 25 results = ~8-13 minutes contextualizer time (vs 30+ min for 77)
    if len(sorted_results) > MAX_RESULTS:
        cutoff_score = sorted_results[MAX_RESULTS - 1].get("score", 0)
        filtered_by_score = sorted_results[:MAX_RESULTS]
        discarded_count = len(sorted_results) - len(filtered_by_score)

        logger.info(
            f"[RESEARCHER] Score filter: {len(sorted_results)} → {len(filtered_by_score)} "
            f"(cutoff score: {cutoff_score:.3f}, discarded: {discarded_count})"
        )

        # Log what's being discarded (sample)
        discarded_sample = sorted_results[
            MAX_RESULTS : MAX_RESULTS + DISCARD_SAMPLE_SIZE
        ]
        if discarded_sample:
            logger.info("[RESEARCHER] Sample discarded results:")
            for r in discarded_sample:
                score = r.get("score", 0)
                title = r.get("title", "")[:40]
                logger.info(f"    [score: {score:.3f}] {title}...")

        logger.info(
            f"[RESEARCHER] Final count for contextualizer: {len(filtered_by_score)} documents"
        )
        return filtered_by_score

    logger.info(
        f"[RESEARCHER] Score filter: {len(sorted_results)} {source_description} "
        f"(all results kept, below MAX_RESULTS={MAX_RESULTS})"
    )
    logger.info(
        f"[RESEARCHER] Final count for contextualizer: {len(sorted_results)} documents"
    )
    return sorted_results


def sort_and_deduplicate(all_results: list) -> list:
    """Sort results by score and deduplicate by URL.

    Args:
        all_results: Raw search results from multiple queries

    Returns:
        Unique results sorted by score (descending)
    """
    # Deduplicate by URL
    seen_urls = set()
    unique_results = []
    for result in all_results:
        url = result.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_results.append(result)

    if unique_results:
        logger.info(
            f"[RESEARCHER] After deduplication: {len(unique_results)} unique results"
        )

    # Sort by SearXNG score (descending) - higher score = better relevance
    sorted_results = sorted(
        unique_results, key=lambda r: r.get("score", 0), reverse=True
    )

    return sorted_results
