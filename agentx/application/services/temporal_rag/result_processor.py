"""Result processing for temporal RAG.

Handles fact invalidation and result weighting.
"""

from agentx.domain.entities.enums import TemporalType


def invalidate_outdated_facts(results: list[dict]) -> list[dict]:
    """Mark outdated facts in results.

    Args:
        results: Search results.

    Returns:
        list[dict]: Results with outdated facts marked.
    """
    for result in results:
        metadata = result.get("metadata", {})
        if metadata.get("superseded_by"):
            result["superseded"] = True
        else:
            result["superseded"] = False

    return results


def weight_results(results: list[dict]) -> list[dict]:
    """Weight results by temporal type.

    Args:
        results: Search results.

    Returns:
        list[dict]: Weighted and sorted results.
    """
    # Temporal type weights
    weights = {
        TemporalType.PREFERENCE: 1.5,
        TemporalType.FACT: 1.2,
        TemporalType.EVENT: 1.0,
        TemporalType.STATE: 0.8,
        TemporalType.PLAN: 0.6,
    }

    for result in results:
        temporal_type = result["metadata"].get("temporal_type", TemporalType.FACT)
        base_score = result.get("score", 0.5)
        weight = weights.get(temporal_type, 1.0)
        result["weighted_score"] = base_score * weight

    # Sort by weighted score
    results.sort(key=lambda r: r.get("weighted_score", 0), reverse=True)

    return results
