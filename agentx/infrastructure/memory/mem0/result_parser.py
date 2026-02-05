"""Mem0AI search result parsing utilities."""

import logging


logger = logging.getLogger(__name__)


def parse_search_results(results: object) -> list[str]:
    """Parse Mem0AI search results into list of memory texts.

    Handles multiple result formats from different Mem0AI versions:
    - Dict with "results" key: {"results": [{"memory": "...", ...}]}
    - Direct list: [{"memory": "...", ...}, ...]
    - List of strings: ["memory1", "memory2", ...]

    Args:
        results: Raw results from Mem0AI search

    Returns:
        List of memory text strings
    """
    memories: list[str] = []

    # If results is a dict with "results" key
    if isinstance(results, dict) and "results" in results:
        result_list = results["results"]
    # If results is already a list
    elif isinstance(results, list):
        result_list = results
    else:
        logger.debug(f"Mem0AI search: unexpected format {type(results)}")
        return memories

    # Extract memory text from result items
    for result in result_list:
        if isinstance(result, str):
            memories.append(result)
        elif isinstance(result, dict):
            # Try common keys for memory text
            memory_text = (
                result.get("memory") or result.get("text") or result.get("content")
            )
            if memory_text:
                memories.append(memory_text)

    return memories
