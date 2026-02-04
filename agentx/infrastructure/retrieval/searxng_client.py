"""SearXNG client for web search."""


class SearXNGClient:
    """Client for SearXNG metasearch engine."""

    def __init__(self, url: str) -> None:
        """Initialize the SearXNG client.

        Args:
            url: SearXNG server URL

        Raises:
            NotImplementedError: If not yet implemented
        """
        raise NotImplementedError("SearXNGClient not yet implemented")

    async def search(self, query: str, num_results: int = 10) -> list[dict]:
        """Search SearXNG and return results.

        Args:
            query: Search query
            num_results: Number of results

        Returns:
            List of search results

        Raises:
            NotImplementedError: If not yet implemented
        """
        raise NotImplementedError("SearXNGClient.search() not yet implemented")
