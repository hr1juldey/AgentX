# =============================================================================
# AGENTX Researcher - Web Fetcher Service
# =============================================================================
# Pure service for fetching and parsing web pages (not a DSPy module)
# =============================================================================

import asyncio
import logging
from typing import Optional

import httpx
from bs4 import BeautifulSoup
import html2text

logger = logging.getLogger(__name__)

# Configure html2text for markdown conversion
H2T = html2text.HTML2Text()
H2T.ignore_links = False
H2T.ignore_images = False
H2T.body_width = 0  # Don't wrap lines
H2T.unicode_snob = True


async def fetch_page(url: str, timeout: float = 15.0) -> Optional[dict]:
    """Fetch a single web page and convert to markdown.

    Args:
        url: URL to fetch
        timeout: Request timeout in seconds

    Returns:
        Dict with url, title, markdown_content, links (list of dicts)
        or None if fetch fails
    """
    headers = {"User-Agent": "Mozilla/5.0 (compatible; AgentX/1.0; +https://agentx.ai)"}

    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.text, "html.parser")

            # Extract title - handle None from soup.title.string
            title_str: Optional[str] = None
            if soup.title and soup.title.string:
                title_str = str(soup.title.string)
            title = title_str if title_str else url

            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()

            # Convert to markdown
            html_content = str(soup.body) if soup.body else response.text
            markdown_content = H2T.handle(html_content)

            # Extract links (limit to first 50 to avoid bloat)
            links = []
            for a_tag in soup.find_all("a", href=True)[:50]:
                href_attr = a_tag.get("href")
                # Convert to string and check if it's a valid HTTP URL
                if href_attr:
                    href = str(href_attr)
                    if href.startswith("http"):
                        links.append(
                            {
                                "url": href,
                                "text": a_tag.get_text(strip=True)[:100],
                            }
                        )

            logger.info(
                f"Fetched {url}: {len(markdown_content)} chars, {len(links)} links"
            )

            return {
                "url": url,
                "title": title.strip() if isinstance(title, str) else str(title),
                "markdown_content": markdown_content,
                "links": links,
            }

    except Exception as e:
        logger.warning(f"Failed to fetch {url}: {e}")
        return None


async def fetch_multiple_pages(urls: list[str]) -> list[dict]:
    """Fetch multiple pages concurrently.

    Args:
        urls: List of URLs to fetch

    Returns:
        List of page data dicts (excluding failed fetches)
    """
    tasks = [fetch_page(url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Filter out None values and exceptions
    pages = []
    for result in results:
        if isinstance(result, Exception):
            logger.warning(f"Fetch error: {result}")
            continue
        if result is not None:
            pages.append(result)

    logger.info(f"Fetched {len(pages)}/{len(urls)} pages successfully")
    return pages


def truncate_content(content: str, max_chars: int = 2000) -> str:
    """Truncate content to max characters, preserving sentence boundaries.

    Args:
        content: Content to truncate
        max_chars: Maximum characters to keep

    Returns:
        Truncated content
    """
    if len(content) <= max_chars:
        return content

    # Try to truncate at sentence boundary
    truncated = content[:max_chars]
    last_period = truncated.rfind(".")
    last_newline = truncated.rfind("\n")

    # Use the later boundary
    cut_point = max(last_period, last_newline)
    if cut_point > max_chars // 2:  # Ensure we keep at least half
        return content[: cut_point + 1]

    return truncated + "..."
