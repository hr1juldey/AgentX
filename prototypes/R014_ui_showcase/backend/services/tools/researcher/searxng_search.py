# =============================================================================
# AGENTX Researcher - SearXNG Search Module
# =============================================================================
# Searches SearXNG for live web data
# =============================================================================

import asyncio
from typing import Optional

import dspy
import httpx


class SearXNGSearchModule(dspy.Module):
    """Searches SearXNG for live web data.

    Has 3 signatures:
    - SearchGeneral: General web search
    - SearchImages: Image search
    - SearchNews: News search
    """

    def __init__(self, searxng_url: str = "http://192.168.1.4:8080"):
        super().__init__()
        self.searxng_url = searxng_url
        self.search_general = dspy.Predict("query -> search_results")
        self.client = httpx.AsyncClient(timeout=30.0)

    async def _search_searxng(
        self,
        query: str,
        categories: Optional[list[str]] = None,
        engines: Optional[list[str]] = None,
    ) -> list[dict]:
        """Execute SearXNG search."""
        params = {
            "q": query,
            "format": "json",
        }

        if categories:
            params["categories"] = ",".join(categories)
        if engines:
            params["engines"] = ",".join(engines)

        try:
            response = await self.client.get(
                f"{self.searxng_url}/search",
                params=params,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])
        except Exception as e:
            print(f"SearXNG search error: {e}")
            return []

    def forward(self, query: str, search_type: str = "general") -> dict:
        """Execute search based on type.

        Args:
            query: Search query
            search_type: Type of search (general, images, news)

        Returns:
            Search results with URL list for OpenGraph rendering
        """
        # Determine categories based on search_type
        categories = None
        if search_type == "news":
            categories = ["news"]

        # Run async search in sync context
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Create new loop in thread
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run,
                    self._search_searxng(query, categories),
                )
                results = future.result()
        else:
            results = asyncio.run(self._search_searxng(query, categories))

        # Extract URLs for OpenGraph rendering (not images!)
        url_list = []
        for result in results:
            url = result.get("url", "")
            if url and url.startswith("http"):
                url_list.append(
                    {
                        "url": url,
                        "title": result.get("title", ""),
                        "snippet": result.get("content", "")[:200],
                        "source": result.get("source", ""),
                        "engine": result.get("engine", ""),
                    }
                )

        return {
            "raw_data": results,
            "query": query,
            "search_type": search_type,
            "url_list": url_list,  # URLs for OpenGraph rendering
        }
