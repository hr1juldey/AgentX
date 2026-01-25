# =============================================================================
# AGENTX Master Agent - Research Result Merger
# =============================================================================
# Merges additional research results with first research results
# =============================================================================

from typing import Any, List

from services.pipeline.presenter_modules.result_builder import (
    PresenterResultBuilder,
)


def _deduplicate_by_url(
    base_items: List[dict], additional_items: List[dict]
) -> List[dict]:
    """Deduplicate items by URL field.

    Args:
        base_items: Base list of items with 'url' field
        additional_items: Additional items to deduplicate against base

    Returns:
        Unique additional items (not in base_items)
    """
    seen_urls = {item.get("url", "") for item in base_items if item.get("url")}
    return [item for item in additional_items if item.get("url", "") not in seen_urls]


def _merge_lists(base: List, additional: List) -> List:
    """Merge two lists with deduplication.

    Args:
        base: Base list
        additional: Additional list to extend

    Returns:
        Merged list
    """
    return PresenterResultBuilder._ensure_list(
        base
    ) + PresenterResultBuilder._ensure_list(additional)


def merge_research_results(
    first_result: dict, additional_result: dict
) -> dict[str, Any]:
    """Merge additional research results with first research results.

    Preserves data from first research and adds new data from additional research.
    Arrays are extended, dicts are merged with additional values taking precedence.

    Args:
        first_result: First contextualized research result (primary)
        additional_result: Additional contextualized research result

    Returns:
        Merged contextualized research result
    """
    merged: dict[str, Any] = {}

    # Merge beautiful_data lists
    first_beautiful = first_result.get("beautiful_data", {})
    additional_beautiful = additional_result.get("beautiful_data", {})
    merged["beautiful_data"] = {
        **first_beautiful,
        "key_facts": _merge_lists(
            first_beautiful.get("key_facts", []),
            additional_beautiful.get("key_facts", []),
        ),
        "trends": _merge_lists(
            first_beautiful.get("trends", []),
            additional_beautiful.get("trends", []),
        ),
        "comparisons": _merge_lists(
            first_beautiful.get("comparisons", []),
            additional_beautiful.get("comparisons", []),
        ),
    }

    # Merge contextualized_data with URL deduplication
    first_docs = first_result.get("contextualized_data", [])
    additional_docs = additional_result.get("contextualized_data", [])
    merged["contextualized_data"] = first_docs + _deduplicate_by_url(
        first_docs, additional_docs
    )

    # Merge citations with URL deduplication
    first_citations = first_result.get("citations", [])
    additional_citations = additional_result.get("citations", [])
    merged["citations"] = first_citations + _deduplicate_by_url(
        first_citations, additional_citations
    )

    # Merge url_list with deduplication
    first_urls = first_result.get("url_list", [])
    additional_urls = additional_result.get("url_list", [])
    merged["url_list"] = list(set(first_urls + additional_urls))

    # Merge documents with URL deduplication
    first_documents = first_result.get("documents", [])
    additional_documents = additional_result.get("documents", [])
    merged["documents"] = first_documents + _deduplicate_by_url(
        first_documents, additional_documents
    )

    # Preserve processing artifacts from first research
    merged["ranked_data"] = first_result.get("ranked_data", [])
    merged["filtered_data"] = first_result.get("filtered_data", [])
    merged["removed_count"] = first_result.get("removed_count", 0)
    merged["query_relevance"] = first_result.get("query_relevance", "Medium")

    # Preserve structured_report (fallback to additional if first is empty)
    merged["structured_report"] = first_result.get(
        "structured_report", ""
    ) or additional_result.get("structured_report", "")

    return merged
