"""Search Executor Module for Researcher agent.

Ported from R014: services/tools/researcher/search_executor.py

Executes web searches using SearXNG with async wrapper.
Provides configurable search with domain-specific optimization.
"""

import httpx
from typing import Any

from agentx.core.config import get_settings


class SearchExecutorModule:
    """Executes web searches using SearXNG.

    Provides async search interface with:
    - Multiple search engines via SearXNG
    - Domain-specific optimization
    - Configurable result count
    - Error handling and retries
    """

    def __init__(self) -> None:
        """Initialize the search executor."""
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

            # Extract results
            results = self._extract_results(data, num_results)

            return {
                "results": results,
                "query": query,
                "total_results": len(results),
            }

        except httpx.TimeoutException:
            return {
                "results": [],
                "query": query,
                "error": "Search timed out",
            }
        except httpx.HTTPError as e:
            return {
                "results": [],
                "query": query,
                "error": f"Search failed: {e}",
            }
        except Exception as e:
            return {
                "results": [],
                "query": query,
                "error": f"Unexpected error: {e}",
            }

    def _extract_results(self, data: dict, num_results: int) -> list[dict]:
        """Extract and format search results.

        Args:
            data: Raw SearXNG response JSON
            num_results: Maximum number of results to return

        Returns:
            list of dict with title, url, snippet, published_date
        """
        results = []

        # Extract results from SearXNG response
        raw_results = data.get("results", [])

        for item in raw_results[:num_results]:
            result = {
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "snippet": item.get("content", ""),
                "published_date": self._parse_date(item),
                "engine": item.get("engine", "unknown"),
                "score": item.get("score", 0.0),
            }
            results.append(result)

        return results

    def _parse_date(self, item: dict) -> str:
        """Parse publication date from SearXNG result.

        Args:
            item: SearXNG result item

        Returns:
            str: Date in YYYY-MM-DD format, or 'n.d.' if not found
        """
        # Try to extract date from publication date field
        pub_date = item.get("publishedDate", "")
        if pub_date:
            return pub_date

        # Try to extract from metadata
        metadata = item.get("metadata", {})
        if "date" in metadata:
            return metadata["date"]

        # Default to no date
        return "n.d."

    async def batch_search(
        self, queries: list[str], num_results: int = 5
    ) -> dict[str, Any]:
        """Execute multiple searches in batch.

        Args:
            queries: List of search queries
            num_results: Number of results per query

        Returns:
            dict with 'all_results' (dict mapping query to results)
        """
        all_results = {}

        for query in queries:
            result = await self.search(query, num_results)
            all_results[query] = result

        return {
            "all_results": all_results,
            "total_queries": len(queries),
        }
