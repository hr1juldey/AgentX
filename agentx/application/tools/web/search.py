"""Web search tools for DSPy agents."""

import dspy


def searxng_search(query: str) -> str:
    """Search SearXNG and return results.

    Args:
        query: Search query

    Returns:
        Search results as string

    Raises:
        NotImplementedError: If not yet implemented
    """
    raise NotImplementedError("searxng_search() not yet implemented")


# Create DSPy tool wrapper
searxng_search_tool = dspy.Tool(searxng_search, name="searxng_search")
