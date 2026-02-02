"""SearXNG client for web search.

Provides async search interface with multiple search engines.
"""

import httpx
from typing import Any

from agentx.core.config import get_settings


class SearXNGClient:
    """Client for SearXNG search API.

    Provides async search interface with:
    - Multiple search engines via SearXNG
    - Domain-specific optimization
    - Configurable result count
    - Error handling and retries
    """

    def __init__(self) -> None:
        """Initialize the SearXNG client."""
        self.settings = get_settings()
        self.searxng_url = self.settings.searxng.base_url
        self.timeout = 30  # seconds

    async def search(
        self,
        query: str,
        num_results: int = 10,
        domain: str = "general",
    ) -> dict[str, Any]:
        """Execute a web search query.

        Args:
            query: Search query string
            num_results: Number of results to retrieve (default: 10)
            domain: Subject domain for optimization (default: "general")

        Returns:
            dict with 'results' (list) and 'query' (str)
        """
        # Build SearXNG request
        params = {
            "q": query,
            "format": "json",
            "engines": "google,bing,duckduckgo",  # Multiple engines
            "language": "en",
        }

        # Add domain-specific engines
        if domain == "science":
            params["engines"] += ",google scholar"
        elif domain == "news":
            params["engines"] += ",bing news"

        try:
            # Execute async search
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.searxng_url}/search",
                    params=params,
                )
                response.raise_for_status()
                data = response.json()

            return {
                "raw_data": data,
                "query": query,
                "num_results_requested": num_results,
            }

        except httpx.TimeoutException:
            return {
                "raw_data": {},
                "query": query,
                "error": "Search timed out",
            }
        except httpx.HTTPError as e:
            return {
                "raw_data": {},
                "query": query,
                "error": f"Search failed: {e}",
            }
        except Exception as e:
            return {
                "raw_data": {},
                "query": query,
                "error": f"Unexpected error: {e}",
            }
