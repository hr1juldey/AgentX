# =============================================================================
# AGENTX R013 - Search Service
# =============================================================================
# SearXNG integration for travel information retrieval
# =============================================================================

import logging

import httpx
from config.settings import settings

logger = logging.getLogger(__name__)


async def search_travel(query: str) -> str:
    """Search SearXNG and return contextualized results.

    Args:
        query: Search query for travel information

    Returns:
        Contextualized search results as string
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            params = {
                "q": query,
                "format": "json",
                "engines": "google,bing,duckduckgo",
            }

            response = await client.get(
                f"{settings.searxng_url}/search",
                params=params,
            )
            response.raise_for_status()
            results = response.json()

        # Extract top results
        snippets: list[str] = []
        for r in results.get("results", [])[:5]:
            title = r.get("title", "")
            content = r.get("content", "")
            # Use format for proper string type
            snippet = str(title) + ": " + str(content)
            snippets.append(snippet)

        return "\n".join(snippets)

    except httpx.HTTPError as e:
        logger.error(f"SearXNG search failed: {e}")
        return "Search currently unavailable."


def search_travel_sync(query: str) -> str:
    """Synchronous wrapper for search_travel (for ReAct tools).

    This handles the case where ReAct tools run in a thread without an event loop.

    Args:
        query: Search query for travel information

    Returns:
        Contextualized search results as string
    """
    import asyncio

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, search_travel(query))
                return future.result()
        else:
            return loop.run_until_complete(search_travel(query))
    except RuntimeError:
        # No event loop exists, create a new one
        return asyncio.run(search_travel(query))
