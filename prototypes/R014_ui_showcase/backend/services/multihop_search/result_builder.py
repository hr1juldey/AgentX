# =============================================================================
# AGENTX Multi-Hop Search - Result Builder
# =============================================================================
# Builds final search results from hop data
# =============================================================================

from __future__ import annotations

from typing import Any

import dspy


def build_search_result(
    final_result: dspy.Prediction,
    hop_answers: list[str],
    hop_queries: list[str],
    hop_num: int,
    total_elapsed: float,
) -> dspy.Prediction:
    """Build final search result prediction.

    Args:
        final_result: Final synthesis result
        hop_answers: Accumulated hop answers
        hop_queries: Accumulated search queries
        hop_num: Total hops executed
        total_elapsed: Total time elapsed

    Returns:
        Complete prediction with all metadata
    """
    return dspy.Prediction(
        answer=final_result.final_answer,  # type: ignore[missing-attribute]
        summary=final_result.summary,  # type: ignore[missing-attribute]
        confidence=final_result.confidence,  # type: ignore[missing-attribute]
        citations=_extract_citations(hop_answers),
        hops=_build_hops(hop_queries, hop_answers),
        metadata={
            "total_time": total_elapsed,
            "num_hops": hop_num,
            "queries_used": hop_queries,
        },
    )


def _extract_citations(hop_answers: list[str]) -> list[dict[str, Any]]:
    """Extract citations from hop answers."""
    citations: list[dict[str, Any]] = []
    for hop_result in hop_answers:
        if hasattr(hop_result, "sources_summary"):
            citations.append({"summary": hop_result.sources_summary})
    return citations


def _build_hops(hop_queries: list[str], hop_answers: list[str]) -> list[dict[str, Any]]:
    """Build hop records from queries and answers."""
    return [
        {
            "hop_number": i + 1,
            "query": hop_queries[i],
            "answer": hop_answers[i],
        }
        for i in range(len(hop_answers))
    ]
