"""Batch search operations.

Executes multiple searches efficiently.
"""

from typing import Any

from agentx.agent.tools.researcher.search.searxng_client import SearXNGClient


class BatchSearchOperations:
    """Handles batch search operations."""

    def __init__(self) -> None:
        """Initialize batch operations with SearXNG client."""
        self._client = SearXNGClient()

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
            result = await self._client.search(query, num_results)
            all_results[query] = result

        return {
            "all_results": all_results,
            "total_queries": len(queries),
        }
