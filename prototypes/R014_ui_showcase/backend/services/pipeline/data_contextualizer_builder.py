# =============================================================================
# AGENTX DATA CONTEXTUALIZER Builder Utilities
# =============================================================================
# Helper functions for building contextualizer return dict
# =============================================================================

from typing import Any, Dict


def build_contextualized_return(
    ranked_result: dict,
    filtered_result: dict,
    contextualized_result: dict,
    beautiful_data: dict,
    contextualized_data_final: list,
    top_facts: list,
    research_data: dict,
) -> Dict[str, Any]:
    """Build the contextualized return dictionary.

    Args:
        ranked_result: Result from reranker
        filtered_result: Result from filter
        contextualized_result: Result from contextualizer
        beautiful_data: Beautiful data from research
        contextualized_data_final: Final contextualized data
        top_facts: Extracted top facts
        research_data: Original research data

    Returns:
        Complete contextualized result dict
    """
    return {
        "ranked_data": ranked_result.get("ranked_data", [])
        if hasattr(ranked_result, "get")
        else [],
        "relevance_scores": ranked_result.get("scores", [])
        if hasattr(ranked_result, "get")
        else [],
        "filtered_data": filtered_result.get("filtered_data", [])
        if hasattr(filtered_result, "get")
        else [],
        "removed_count": filtered_result.get("removed_count", 0)
        if hasattr(filtered_result, "get")
        else 0,
        "contextualized_data": contextualized_data_final,
        "query_relevance": contextualized_result.get("query_relevance", "Medium")
        if hasattr(contextualized_result, "get")
        else "Medium",
        "beautiful_data": {
            **beautiful_data,
            "top_facts": top_facts,
        },
        # Preserve original research data for hydrators
        "structured_report": research_data.get("structured_report", ""),
        "structured_data": research_data.get("structured_data", {}),
        "query": research_data.get("query", ""),
        "citations": research_data.get("citations", []),
        "url_list": research_data.get("url_list", []),
        "documents": research_data.get("documents", []),
        "search_terms": research_data.get("search_terms", []),
    }
