"""HTTP client for web scraping.

Handles HTTP requests with error handling and timeout.
"""

import httpx
from bs4 import BeautifulSoup
from typing import Any


class HTTPClient:
    """HTTP client for web scraping."""

    def __init__(self, timeout: int = 30) -> None:
        """Initialize HTTP client.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.user_agent = "Mozilla/5.0 (compatible; AgentX/0.1; +https://agentx.ai)"

    async def fetch_url(self, url: str) -> dict[str, Any]:
        """Fetch HTML from a URL.

        Args:
            url: URL to fetch

        Returns:
            dict with 'html' (str), 'url' (str), 'status_code' (int), 'error' (str)
        """
        headers = {"User-Agent": self.user_agent}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=headers, follow_redirects=True)
                response.raise_for_status()
                html = response.text

            return {
                "html": html,
                "url": url,
                "status_code": response.status_code,
                "error": "",
            }

        except httpx.TimeoutException:
            return {
                "html": "",
                "url": url,
                "status_code": 0,
                "error": "Request timed out",
            }
        except httpx.HTTPError as e:
            return {
                "html": "",
                "url": url,
                "status_code": 0,
                "error": f"HTTP error: {e}",
            }
        except Exception as e:
            return {
                "html": "",
                "url": url,
                "status_code": 0,
                "error": f"Unexpected error: {e}",
            }

    async def fetch_and_parse(
        self, url: str
    ) -> tuple[BeautifulSoup | None, dict[str, Any]]:
        """Fetch and parse HTML from URL.

        Args:
            url: URL to fetch

        Returns:
            tuple of (BeautifulSoup object or None, metadata dict)
        """
        result = await self.fetch_url(url)

        if result["error"]:
            return None, result

        soup = BeautifulSoup(result["html"], "html.parser")
        return soup, result
