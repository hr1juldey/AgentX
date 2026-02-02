"""Search Executor Module for Researcher agent.

Ported from R014: services/tools/researcher/search_executor.py

Executes web searches using SearXNG with async wrapper.
Provides configurable search with domain-specific optimization.

Actual implementation has been moved to the search/ subdirectory.
This facade maintains backward compatibility with existing imports.
"""

from typing import Any

from agentx.agent.tools.researcher.search import (
    BatchSearchOperations,
    SearXNGClient,
    SearchResultParser,
)


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
        self._client = SearXNGClient()
        self._parser = SearchResultParser()
        self._batch_ops = BatchSearchOperations()

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
        search_data = await self._client.search(query, num_results, domain)
        return self._parser.format_search_response(search_data)

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
        return await self._batch_ops.batch_search(queries, num_results)

    def _extract_results(self, data: dict, num_results: int) -> list[dict]:
        """Extract and format search results.

        Args:
            data: Raw SearXNG response JSON
            num_results: Maximum number of results to return

        Returns:
            list of dict with title, url, snippet, published_date
        """
        return self._parser.extract_results(data, num_results)

    def _parse_date(self, item: dict) -> str:
        """Parse publication date from SearXNG result.

        Args:
            item: SearXNG result item

        Returns:
            str: Date in YYYY-MM-DD format, or 'n.d.' if not found
        """
        return self._parser._parse_date(item)
