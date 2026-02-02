"""Batch processing for web scraping.

Handles scraping multiple URLs.
"""

from collections.abc import Callable
from typing import Any


class BatchProcessor:
    """Processes multiple URLs for scraping."""

    def __init__(self, scrape_fn: Callable[[str], Any]) -> None:
        """Initialize batch processor.

        Args:
            scrape_fn: Function to scrape a single URL
        """
        self._scrape_fn = scrape_fn

    async def batch_scrape(self, urls: list[str]) -> dict[str, Any]:
        """Scrape multiple URLs in batch.

        Args:
            urls: List of URLs to scrape

        Returns:
            dict with 'results' (dict mapping url to scraped data)
        """
        results = {}

        for url in urls:
            result = await self._scrape_fn(url)
            results[url] = result

        return {
            "results": results,
            "total_urls": len(urls),
        }
