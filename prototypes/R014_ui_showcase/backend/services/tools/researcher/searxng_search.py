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

from services.tools.researcher.search_async_wrapper import run_async_in_sync_context
from services.tools.researcher.search_domain_priority import (
    aggregate_and_prioritize_results,
)
from services.tools.researcher.search_result_processor import extract_url_list

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
        # Engine groups to try in parallel (some may be blocked/rate-limited)
        self.engine_groups = [
            # Reliable engines that usually work
            ["bing", "mojeek", "yahoo", "ask"],
            # Google (may have rate limits)
            ["google"],
            # Alternative engines
            ["brave", "startpage"],
            # DuckDuckGo often shows CAPTCHA but worth trying
            ["duckduckgo"],
        ]

    async def _search_with_engines(
        self,
        query: str,
        engines: list[str],
        categories: Optional[list[str]] = None,
        image_search: bool = False,
    ) -> list[dict]:
        """Execute SearXNG search with specific engine list."""
        params = {
            "q": query,
            "format": "json",
            "engines": ",".join(engines),
        }

        # Image search uses category_images=1, NOT categories=images
        if image_search:
            params["category_images"] = "1"
        elif categories:
            params["categories"] = ",".join(categories)

        try:
            url = f"{self.searxng_url}/search"
            logger.info(f"[SearXNG] Trying engines: {engines}")
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                results = data.get("results", [])
                logger.info(f"[SearXNG] Engines {engines[0]}: {len(results)} results")
                return results
        except Exception as e:
            logger.warning(f"[SearXNG] Engines {engines[0]} failed: {e}")
            return []

    async def _search_searxng(
        self,
        query: str,
        categories: Optional[list[str]] = None,
        engines: Optional[list[str]] = None,
        image_search: bool = False,
    ) -> list[dict]:
        """Execute SearXNG search with parallel engine groups.

        Tries multiple engine groups in parallel and aggregates results.
        This handles engines that may be blocked or rate-limited.
        """
        # If specific engines requested, use only those
        if engines:
            return await self._search_with_engines(
                query, engines, categories, image_search
            )

        # Otherwise, try all engine groups in parallel
        tasks = [
            self._search_with_engines(query, group, categories, image_search)
            for group in self.engine_groups
        ]

        # Run all searches in parallel and wait for all to complete
        all_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Aggregate and prioritize results using helper
        aggregated = aggregate_and_prioritize_results(all_results)

        logger.info(f"[SearXNG] Total aggregated results: {len(aggregated)}")
        return aggregated

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
        results = run_async_in_sync_context(
            self._search_searxng(query, categories, image_search=image_search)
        )

        # Extract URLs for OpenGraph rendering
        url_list = extract_url_list(results, image_search)

        return {
            "raw_data": results,
            "query": query,
            "search_type": search_type,
            "url_list": url_list,  # URLs for OpenGraph rendering
        }
