"""Web Scraper Module for Researcher agent.

Ported from R014: services/tools/researcher/web_scraper.py

Provides web scraping capabilities for extracting main content
from URLs. Uses beautifulsoup4 for HTML parsing.
"""

import httpx
from bs4 import BeautifulSoup
from typing import Any


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
        self.timeout = 30  # seconds
        self.user_agent = "Mozilla/5.0 (compatible; AgentX/0.1; +https://agentx.ai)"

    async def scrape_url(self, url: str) -> dict[str, Any]:
        """Scrape content from a URL.

        Args:
            url: URL to scrape

        Returns:
            dict with 'html' (str), 'text' (str), 'title' (str), 'error' (str)
        """
        headers = {"User-Agent": self.user_agent}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=headers, follow_redirects=True)
                response.raise_for_status()
                html = response.text

            # Parse HTML
            soup = BeautifulSoup(html, "html.parser")

            # Extract metadata
            title = self._extract_title(soup)
            main_content = self._extract_main_content(soup)

            return {
                "html": html,
                "text": main_content,
                "title": title,
                "url": url,
                "status_code": response.status_code,
                "error": "",
            }

        except httpx.TimeoutException:
            return {
                "html": "",
                "text": "",
                "title": "",
                "url": url,
                "error": "Request timed out",
            }
        except httpx.HTTPError as e:
            return {
                "html": "",
                "text": "",
                "title": "",
                "url": url,
                "error": f"HTTP error: {e}",
            }
        except Exception as e:
            return {
                "html": "",
                "text": "",
                "title": "",
                "url": url,
                "error": f"Unexpected error: {e}",
            }

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract title from HTML.

        Args:
            soup: BeautifulSoup object

        Returns:
            str: Page title
        """
        # Try h1 tag first
        h1 = soup.find("h1")
        if h1:
            return h1.get_text(strip=True)

        # Try title tag
        title = soup.find("title")
        if title:
            return title.get_text(strip=True)

        # Try meta og:title
        meta_title = soup.find("meta", property="og:title")
        if meta_title:
            content = meta_title.get("content", "")
            return str(content) if content else ""

        # Default
        return "Untitled"

    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from HTML.

        Args:
            soup: BeautifulSoup object

        Returns:
            str: Main content text
        """
        # Remove unwanted elements
        for element in soup(
            [
                "script",
                "style",
                "nav",
                "header",
                "footer",
                "aside",
                "iframe",
                "noscript",
            ]
        ):
            element.decompose()

        # Try to find main content area
        main_content = (
            soup.find("main")
            or soup.find("article")
            or soup.find("div", class_="content")
            or soup.find("div", class_="main")
            or soup.body
        )

        if main_content:
            # Get all paragraphs
            paragraphs = main_content.find_all("p")
            text = "\n\n".join(
                p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)
            )
            return text

        # Fallback: get all text
        return soup.get_text(separator="\n", strip=True)

    async def batch_scrape(self, urls: list[str]) -> dict[str, Any]:
        """Scrape multiple URLs in batch.

        Args:
            urls: List of URLs to scrape

        Returns:
            dict with 'results' (dict mapping url to scraped data)
        """
        results = {}

        for url in urls:
            result = await self.scrape_url(url)
            results[url] = result

        return {
            "results": results,
            "total_urls": len(urls),
        }
