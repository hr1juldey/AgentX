# =============================================================================
# AGENTX Multi-Hop Search - SearXNG Client
# =============================================================================
# SearXNG client for privacy-focused web search
# =============================================================================

from __future__ import annotations

import logging
from dataclasses import dataclass

import httpx

logger = logging.getLogger(__name__)


@dataclass
class SearchResultItem:
    """Individual search result from SearXNG."""

    url: str
    title: str
    content: str
    engine: str
    score: float
    category: str = "general"


class SearXNGClient:
    """SearXNG client for web search.

    Uses SearXNG privacy-focused metasearch engine.
    Default URL: http://192.168.1.4:8080 (configured in settings)
    """

    def __init__(self, base_url: str, timeout: float = 10.0) -> None:
        """Initialize SearXNG client.

        Args:
            base_url: SearXNG instance base URL
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def search(
        self,
        query: str,
        max_results: int = 10,
    ) -> list[SearchResultItem]:
        """Perform web search and return results.

        Args:
            query: Search query string
            max_results: Maximum number of results to return

        Returns:
            List of search results
        """
        params = {
            "q": query,
            "format": "json",
            "engines": "google,bing,duckduckgo",
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/search",
                    params=params,
                )
                response.raise_for_status()
                data = response.json()

            # Parse results
            results: list[SearchResultItem] = []
            for result in data.get("results", [])[:max_results]:
                results.append(
                    SearchResultItem(
                        url=result.get("url", ""),
                        title=result.get("title", ""),
                        content=result.get("content", ""),
                        engine=result.get("engine", ""),
                        score=result.get("score", 0.0),
                        category=result.get("category", "general"),
                    )
                )

            logger.info(
                f"SearXNG returned {len(results)} results for query: '{query[:50]}...'"
            )
            return results

        except httpx.HTTPError as e:
            logger.error(f"SearXNG search failed: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error during search: {e}")
            return []


# Global client instance
_search_client: SearXNGClient | None = None


def get_search_client(base_url: str) -> SearXNGClient:
    """Get or create global SearXNG client.

    Args:
        base_url: SearXNG instance base URL

    Returns:
        SearXNG client instance
    """
    global _search_client
    if _search_client is None:
        _search_client = SearXNGClient(base_url)
    return _search_client
