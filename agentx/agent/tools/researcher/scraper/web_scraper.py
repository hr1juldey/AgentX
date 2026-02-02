"""Web Scraper Module for Researcher agent.

Composes HTTP client, content extractor, and batch processor.
"""

from typing import Any

from agentx.agent.tools.researcher.scraper.batch_processor import BatchProcessor
from agentx.agent.tools.researcher.scraper.content_extractor import ContentExtractor
from agentx.agent.tools.researcher.scraper.http_client import HTTPClient


class WebScraperModule:
    """Web scraper for extracting main content from URLs.

    Provides:
    - URL scraping with error handling
    - Main content extraction (removes navigation, ads, etc.)
    - Text extraction from HTML
    - Metadata extraction (title, date, author)
    """

    def __init__(self) -> None:
        """Initialize the web scraper."""
        self._http_client = HTTPClient()
        self._extractor = ContentExtractor()
        self._batch = BatchProcessor(self.scrape_url)

    async def scrape_url(self, url: str) -> dict[str, Any]:
        """Scrape content from a URL.

        Args:
            url: URL to scrape

        Returns:
            dict with 'html' (str), 'text' (str), 'title' (str), 'error' (str)
        """
        soup, metadata = await self._http_client.fetch_and_parse(url)

        if soup is None:
            return {
                "html": metadata.get("html", ""),
                "text": "",
                "title": "",
                "url": url,
                "error": metadata.get("error", "Unknown error"),
            }

        content = self._extractor.extract_all(soup)

        return {
            "html": metadata.get("html", ""),
            "text": content["text"],
            "title": content["title"],
            "url": url,
            "status_code": metadata.get("status_code", 0),
            "error": "",
        }

    async def batch_scrape(self, urls: list[str]) -> dict[str, Any]:
        """Scrape multiple URLs in batch.

        Args:
            urls: List of URLs to scrape

        Returns:
            dict with 'results' (dict mapping url to scraped data)
        """
        return await self._batch.batch_scrape(urls)
