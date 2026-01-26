# =============================================================================
# AGENTX Researcher Search Execution
# =============================================================================
# Executes SearXNG searches and aggregates results
# =============================================================================

import logging

logger = logging.getLogger(__name__)


# Constants
MAX_QUERY_DISPLAY = 3


def execute_multi_term_search(
    searcher,
    search_terms: list,
) -> tuple:
    """Execute multiple searches and aggregate results.

    Args:
        searcher: SearXNGSearchModule instance
        search_terms: List of search terms to query

    Returns:
        Tuple of (aggregated_results, query_display_string, url_list)
    """
    all_results = []
    url_list = []
    for term in search_terms:
        search_results_raw = searcher(query=term, search_type="general")
        search_results = (
            search_results_raw if hasattr(search_results_raw, "get") else {}
        )
        term_results = search_results.get("raw_data", [])
        term_urls = search_results.get("url_list", [])
        logger.info(
            f"[RESEARCHER] Term '{term[:30]}...' got {len(term_results)} results"
        )
        all_results.extend(term_results)
        url_list.extend(term_urls)

    query_display = (
        f"{len(search_terms)} terms: {', '.join(search_terms[:MAX_QUERY_DISPLAY])}"
    )
    return all_results, query_display, url_list


def execute_single_search(
    searcher,
    query: str,
) -> tuple:
    """Execute a single search query.

    Args:
        searcher: SearXNGSearchModule instance
        query: Search query string

    Returns:
        Tuple of (search_results, query_display_string, url_list)
    """
    search_results_raw = searcher(query=query, search_type="general")
    search_results = search_results_raw if hasattr(search_results_raw, "get") else {}
    raw_results = (
        search_results.get("raw_data", []) if hasattr(search_results, "get") else []
    )
    url_list = search_results.get("url_list", [])

    logger.info(f"[RESEARCHER] Single query got {len(raw_results)} results")
    return raw_results, query, url_list
