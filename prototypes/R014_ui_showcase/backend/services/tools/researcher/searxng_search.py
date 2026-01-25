# =============================================================================
# AGENTX Researcher - SearXNG Search Module
# =============================================================================
# Searches SearXNG for live web data
# =============================================================================

import asyncio
import logging
from typing import Optional

import dspy
import httpx

logger = logging.getLogger(__name__)


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

    async def _search_searxng(
        self,
        query: str,
        categories: Optional[list[str]] = None,
        engines: Optional[list[str]] = None,
        image_search: bool = False,
    ) -> list[dict]:
        """Execute SearXNG search with fresh async client per request."""
        params = {
            "q": query,
            "format": "json",
        }

        # Image search uses category_images=1, NOT categories=images
        if image_search:
            params["category_images"] = "1"
        elif categories:
            params["categories"] = ",".join(categories)

        if engines:
            params["engines"] = ",".join(engines)

        try:
            logger.info(f"[SearXNG] Searching: {query[:60]}...")
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.searxng_url}/search",
                    params=params,
                )
                response.raise_for_status()
                data = response.json()
                results = data.get("results", [])
                logger.info(f"[SearXNG] Got {len(results)} results")
                return results
        except Exception as e:
            logger.error(f"[SearXNG] Search error for '{query[:40]}...': {e}")
            return []

    def forward(self, query: str, search_type: str = "general") -> dict:
        """Execute search based on type.

        Args:
            query: Search query
            search_type: Type of search (general, images, news)

        Returns:
            Search results with URL list for OpenGraph rendering
        """
        # Determine categories and image search based on search_type
        categories = None
        image_search = False

        if search_type == "news":
            categories = ["news"]
        elif search_type == "images":
            image_search = True

        # Run async search in sync context
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Create new loop in thread
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run,
                    self._search_searxng(query, categories, image_search=image_search),
                )
                results = future.result()
        else:
            results = asyncio.run(
                self._search_searxng(query, categories, image_search=image_search)
            )

        # Extract URLs for OpenGraph rendering
        url_list = []
        for result in results:
            # For image search, extract img_src (the actual image URL)
            # For general/news, extract the page URL
            if image_search:
                url = result.get("img_src", "")
            else:
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
