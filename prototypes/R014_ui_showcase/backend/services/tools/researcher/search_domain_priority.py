# =============================================================================
# AGENTX Researcher - Search Domain Priority
# =============================================================================
# Domain priority scoring for authoritative sources
# =============================================================================

from typing import Any


def get_domain_priority(url: str) -> int:
    """Calculate domain priority for authoritative sources.

    Higher priority = better source (0=low, 3=high).

    Priority levels:
    - 3: Government, education, major research institutions (.gov, .edu, .org)
    - 2: News, research, academic sources
    - 1: Default (general websites)
    - 0: Forums, social media, Q&A sites

    Args:
        url: URL to prioritize

    Returns:
        Priority score (0-3)
    """
    if not url:
        return 0

    url_lower = url.lower()

    # High priority: Government, education, major research institutions
    if any(d in url_lower for d in [".gov", ".edu", ".org"]):
        return 3

    # Medium priority: News, research, academic
    if any(d in url_lower for d in ["research", "academic", "news", "analysis"]):
        return 2

    # Low priority: Forums, social media, Q&A sites
    if any(d in url_lower for d in ["forum", "reddit", "quora", "stackexchange"]):
        return 0

    # Default priority
    return 1


def aggregate_and_prioritize_results(all_results: list[Any]) -> list[dict]:
    """Aggregate and deduplicate search results with domain priority sorting.

    Args:
        all_results: List of search result lists from parallel searches

    Returns:
        Aggregated and sorted results
    """
    aggregated = []
    seen_urls = set()  # Deduplicate by URL

    for result in all_results:
        if isinstance(result, Exception):
            continue
        if isinstance(result, list):
            for item in result:
                url = item.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    aggregated.append(item)

    # Sort by domain priority (higher priority first)
    aggregated.sort(
        key=lambda item: get_domain_priority(item.get("url", "")), reverse=True
    )

    return aggregated
