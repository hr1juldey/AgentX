# SearXNG Rich Search API Guide

**Source**: Research for AgentX integration
**Topic**: Comprehensive SearXNG API usage for rich search results (images, videos, news, files, etc.)
**Date**: 2026-01-21

---

## Executive Summary

SearXNG is a privacy-focused metasearch engine that aggregates results from multiple search engines (Google, Bing, DuckDuckGo, etc.). It provides a powerful JSON API for programmatic access with support for multiple content types:

- **General Web**: Standard web search results
- **Images**: Image search with thumbnails and full-size URLs
- **Videos**: Video search from multiple platforms
- **News**: News articles with publication dates
- **Science**: Academic and research papers
- **IT/Programming**: Technical content and code
- **Files**: Torrent and file search
- **Social Media**: Social network content
- **Map**: Location-based search

---

## Current Implementations in AgentX

### R013 Travel Planning Stream (Advanced)

**Location**: `prototypes/R013_travel_planning_stream/backend/services/search_service.py`

```python
async def search_travel(query: str) -> str:
    """Search SearXNG and return contextualized results."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        params = {
            "q": query,
            "format": "json",
            "engines": "google,bing,duckduckgo",
        }
        response = await client.get(f"{settings.searxng_url}/search", params=params)
        results = response.json()

        # Extract top 5 results
        snippets = []
        for r in results.get("results", [])[:5]:
            title = r.get("title", "")
            content = r.get("content", "")
            snippets.append(f"{title}: {content}")

        return "\n".join(snippets)
```

**Features**:
- Async/sync dual mode
- Configuration via environment variable
- Error handling with graceful fallback
- DSPy ReAct tool integration

### R011 Personal Assistant (Basic)

**Location**: `prototypes/R011_personal_assistant/backend/services/service.py`

```python
def searxng_search(query: str) -> str:
    """Search using local SearXNG instance."""
    response = requests.get(
        "http://localhost:8080/search",
        params={"q": query, "format": "json"},
        timeout=10,
    )
    data = response.json()

    # Format top 3 results
    results = data["results"][:3]
    formatted = f"Search results for '{query}':\n"
    for i, r in enumerate(results, 1):
        formatted += f"\n{i}. {r.get('title', 'No title')}\n"
        formatted += f"   {r.get('url', 'No URL')}\n"
        if r.get("content"):
            formatted += f"   {r['content'][:200]}...\n"

    return formatted
```

---

## SearXNG API Parameters

### Base URL

```
http://localhost:8080/search
```

### Request Parameters

| Parameter | Type | Required | Values | Description |
|-----------|------|----------|--------|-------------|
| `q` | string | **Yes** | Any text | Search query |
| `format` | string | **Yes** | `json`, `csv`, `rss` | Output format |
| `category` | string | Optional | See below | Search category |
| `engines` | string | Optional | Comma-separated | Specific engines |
| `language` | string | Optional | `en`, `es`, `fr`, `de`, etc. | Search language |
| `safesearch` | int | Optional | `0` (off), `1` (moderate), `2` (strict) | Content filtering |
| `time_range` | string | Optional | `day`, `week`, `month`, `year` | Time filter |
| `pageno` | int | Optional | `1`, `2`, `3`, etc. | Page number |
| `image_proxy` | bool | Optional | `True`, `False` | Proxy images through SearXNG |

### Available Categories

| Category | Description | Example Engines |
|----------|-------------|-----------------|
| `general` | General web search | Google, Bing, DDG, Brave |
| `images` | Image search | Google Images, Bing Images, Qwant Images |
| `videos` | Video search | YouTube, Dailymotion, PeerTube |
| `news` | News articles | Google News, Bing News |
| `science` | Academic papers | arXiv, Semantic Scholar, Crossref |
| `it` | IT/Programming | Github, GitLab, Stack Overflow |
| `files` | Torrent/files | PeerTube, Piped |
| `social_media` | Social content | Mastodon, Lemmy, Matrix |
| `map` | Location search | OpenStreetMap |

---

## JSON Response Format

### Top-Level Response Structure

```json
{
  "query": "search query",
  "number_of_results": 10,
  "results": [...],
  "answers": ["instant answer 1", "instant answer 2"],
  "corrections": ["suggested spelling"],
  "suggestions": ["related query 1", "related query 2"],
  "infoboxes": [...],
  "unresponsive_engines": []
}
```

### General/News Result Fields

```json
{
  "url": "https://example.com/article",
  "title": "Article Title",
  "content": "Snippet or description...",
  "source": "Source Name",
  "publishedDate": "2025-08-20T17:52:00",
  "engine": "google",
  "template": "default.html",
  "parsed_url": ["https", "example.com", "/article", "", "", ""],
  "img_src": "",
  "thumbnail": "",
  "priority": "",
  "engines": ["google", "bing"],
  "positions": [1, 3],
  "score": 1.0,
  "category": "news",
  "pubdate": "2025-08-20 17:52:00"
}
```

### Image Result Fields

```json
{
  "url": "https://example.com/image-page",
  "title": "Image Title",
  "content": "Image description or alt text",
  "img_src": "https://example.com/full-image.jpg",
  "thumbnail_src": "https://example.com/thumb-image.jpg",
  "source": "Website Name",
  "author": "Photographer name",
  "engine": "google images",
  "score": 0.95,
  "category": "images"
}
```

### Video Result Fields

```json
{
  "url": "https://youtube.com/watch?v=xxx",
  "title": "Video Title",
  "content": "Video description",
  "thumbnail": "https://youtube.com/thumb.jpg",
  "template": "default.html",
  "engine": "google videos",
  "score": 0.92,
  "category": "videos"
}
```

### Science/Academic Result Fields

```json
{
  "url": "https://arxiv.org/abs/1234.5678",
  "title": "Paper Title",
  "content": "Abstract...",
  "publishedDate": "2025-01-15",
  "author": "Author Names",
  "doi": "10.1234/example.doi",
  "engine": "arxiv",
  "category": "science",
  "score": 0.88
}
```

---

## Enhanced Search Service Implementation

### Rich Search Service with Multi-Category Support

```python
"""Enhanced SearXNG search service with rich result types."""

import asyncio
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Literal

import httpx

logger = logging.getLogger(__name__)


class SearchCategory(str, Enum):
    """SearXNG search categories."""
    GENERAL = "general"
    IMAGES = "images"
    VIDEOS = "videos"
    NEWS = "news"
    SCIENCE = "science"
    IT = "it"
    FILES = "files"
    SOCIAL_MEDIA = "social_media"
    MAP = "map"


class SafeSearchLevel(int, Enum):
    """Safe search filtering levels."""
    OFF = 0
    MODERATE = 1
    STRICT = 2


class TimeRange(str, Enum):
    """Time range filters."""
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


@dataclass
class SearchResult:
    """Unified search result."""
    url: str
    title: str
    content: str
    category: str
    engine: str
    score: float

    # Optional fields
    thumbnail: str | None = None
    img_src: str | None = None
    published_date: str | None = None
    author: str | None = None
    source: str | None = None
    metadata: dict[str, Any] | None = None


@dataclass
class SearchResponse:
    """Complete SearXNG search response."""
    query: str
    results: list[SearchResult]
    answers: list[str]
    corrections: list[str]
    suggestions: list[str]
    number_of_results: int
    unresponsive_engines: list[str]


class SearXNGClient:
    """Enhanced SearXNG client with rich search support."""

    def __init__(
        self,
        base_url: str = "http://localhost:8080",
        default_language: str = "en",
        default_engines: str = "google,bing,duckduckgo",
        timeout: float = 10.0,
    ):
        """Initialize SearXNG client.

        Args:
            base_url: SearXNG instance URL
            default_language: Default search language
            default_engines: Comma-separated default engines
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.default_language = default_language
        self.default_engines = default_engines
        self.timeout = timeout

    async def search(
        self,
        query: str,
        category: SearchCategory | None = None,
        engines: str | None = None,
        language: str | None = None,
        safesearch: SafeSearchLevel = SafeSearchLevel.MODERATE,
        time_range: TimeRange | None = None,
        page: int = 1,
        image_proxy: bool = True,
    ) -> SearchResponse:
        """Perform a rich search query.

        Args:
            query: Search query string
            category: Search category (images, videos, news, etc.)
            engines: Comma-separated engine names
            language: Language code
            safesearch: Content filtering level
            time_range: Time range filter
            page: Page number for pagination
            image_proxy: Whether to proxy images

        Returns:
            SearchResponse with results and metadata
        """
        params = {
            "q": query,
            "format": "json",
            "language": language or self.default_language,
            "engines": engines or self.default_engines,
            "safesearch": int(safesearch),
            "pageno": page,
            "image_proxy": str(image_proxy).lower(),
        }

        if category:
            params["category"] = category.value
        if time_range:
            params["time_range"] = time_range.value

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/search",
                    params=params,
                )
                response.raise_for_status()
                data = response.json()

            # Parse results
            results = []
            for r in data.get("results", []):
                result = SearchResult(
                    url=r.get("url", ""),
                    title=r.get("title", ""),
                    content=r.get("content", ""),
                    category=r.get("category", "general"),
                    engine=r.get("engine", ""),
                    score=r.get("score", 0.0),
                    thumbnail=r.get("thumbnail") or r.get("thumbnail_src"),
                    img_src=r.get("img_src"),
                    published_date=r.get("publishedDate") or r.get("pubdate"),
                    author=r.get("author"),
                    source=r.get("source"),
                    metadata={
                        "engines": r.get("engines", []),
                        "positions": r.get("positions", []),
                        "parsed_url": r.get("parsed_url", []),
                    },
                )
                results.append(result)

            return SearchResponse(
                query=data.get("query", query),
                results=results,
                answers=data.get("answers", []),
                corrections=data.get("corrections", []),
                suggestions=data.get("suggestions", []),
                number_of_results=data.get("number_of_results", len(results)),
                unresponsive_engines=data.get("unresponsive_engines", []),
            )

        except httpx.HTTPError as e:
            logger.error(f"SearXNG search failed: {e}")
            return SearchResponse(
                query=query,
                results=[],
                answers=[],
                corrections=[],
                suggestions=[],
                number_of_results=0,
                unresponsive_engines=[],
            )

    async def search_images(
        self,
        query: str,
        **kwargs,
    ) -> SearchResponse:
        """Search for images.

        Args:
            query: Image search query
            **kwargs: Additional search parameters

        Returns:
            SearchResponse with image results
        """
        return await self.search(
            query=query,
            category=SearchCategory.IMAGES,
            **kwargs,
        )

    async def search_videos(
        self,
        query: str,
        **kwargs,
    ) -> SearchResponse:
        """Search for videos.

        Args:
            query: Video search query
            **kwargs: Additional search parameters

        Returns:
            SearchResponse with video results
        """
        return await self.search(
            query=query,
            category=SearchCategory.VIDEOS,
            **kwargs,
        )

    async def search_news(
        self,
        query: str,
        time_range: TimeRange | None = None,
        **kwargs,
    ) -> SearchResponse:
        """Search for news articles.

        Args:
            query: News search query
            time_range: Optional time range filter
            **kwargs: Additional search parameters

        Returns:
            SearchResponse with news results
        """
        return await self.search(
            query=query,
            category=SearchCategory.NEWS,
            time_range=time_range,
            **kwargs,
        )

    async def search_science(
        self,
        query: str,
        **kwargs,
    ) -> SearchResponse:
        """Search for academic papers.

        Args:
            query: Academic search query
            **kwargs: Additional search parameters

        Returns:
            SearchResponse with science results
        """
        return await self.search(
            query=query,
            category=SearchCategory.SCIENCE,
            **kwargs,
        )

    async def search_it(
        self,
        query: str,
        **kwargs,
    ) -> SearchResponse:
        """Search for IT/programming content.

        Args:
            query: IT search query
            **kwargs: Additional search parameters

        Returns:
            SearchResponse with IT results
        """
        return await self.search(
            query=query,
            category=SearchCategory.IT,
            **kwargs,
        )

    def format_results_markdown(self, response: SearchResponse, max_results: int = 10) -> str:
        """Format search results as markdown.

        Args:
            response: SearchResponse from search
            max_results: Maximum results to format

        Returns:
            Markdown formatted string
        """
        md = f"# Search Results: {response.query}\n\n"

        # Add instant answers if available
        if response.answers:
            md += "## Quick Answers\n\n"
            for answer in response.answers:
                md += f"- {answer}\n"
            md += "\n"

        # Add spelling corrections
        if response.corrections:
            md += f"**Did you mean:** {response.corrections[0]}\n\n"

        # Add suggestions
        if response.suggestions:
            md += "**Related searches:**\n"
            for suggestion in response.suggestions[:5]:
                md += f"- {suggestion}\n"
            md += "\n"

        # Format results by category
        categories: dict[str, list[SearchResult]] = {}
        for result in response.results[:max_results]:
            cat = result.category
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(result)

        for category, results in categories.items():
            md += f"## {category.title()}\n\n"

            for i, result in enumerate(results, 1):
                md += f"### {i}. {result.title}\n\n"
                md += f"**URL:** {result.url}\n\n"

                if result.author:
                    md += f"**Author:** {result.author} | "
                if result.source:
                    md += f"**Source:** {result.source} | "
                if result.published_date:
                    md += f"**Date:** {result.published_date}"
                md += "\n\n"

                if result.img_src:
                    md += f"**Image:** {result.img_src}\n\n"
                elif result.thumbnail:
                    md += f"**Thumbnail:** {result.thumbnail}\n\n"

                md += f"{result.content}\n\n"
                md += f"*Engine: {result.engine} | Score: {result.score:.2f}*\n\n"
                md += "---\n\n"

        return md


# Singleton client instance
searxng_client = SearXNGClient()


# DSPy tool wrappers
def searxng_search_general(query: str) -> str:
    """Search the web for general information."""
    import asyncio

    async def _search():
        response = await searxng_client.search(query)
        return searxng_client.format_results_markdown(response, max_results=5)

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                return executor.submit(asyncio.run, _search()).result()
        else:
            return loop.run_until_complete(_search())
    except RuntimeError:
        return asyncio.run(_search())


def searxng_search_images(query: str) -> str:
    """Search for images."""
    import asyncio

    async def _search():
        response = await searxng_client.search_images(query)
        return searxng_client.format_results_markdown(response, max_results=10)

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                return executor.submit(asyncio.run, _search()).result()
        else:
            return loop.run_until_complete(_search())
    except RuntimeError:
        return asyncio.run(_search())


def searxng_search_videos(query: str) -> str:
    """Search for videos."""
    import asyncio

    async def _search():
        response = await searxng_client.search_videos(query)
        return searxng_client.format_results_markdown(response, max_results=10)

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                return executor.submit(asyncio.run, _search()).result()
        else:
            return loop.run_until_complete(_search())
    except RuntimeError:
        return asyncio.run(_search())


def searxng_search_news(query: str, time_range: str = "week") -> str:
    """Search for news articles.

    Args:
        query: News search query
        time_range: Time range (day, week, month, year)
    """
    import asyncio

    async def _search():
        time_range_enum = TimeRange(time_range) if time_range else None
        response = await searxng_client.search_news(query, time_range=time_range_enum)
        return searxng_client.format_results_markdown(response, max_results=10)

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                return executor.submit(asyncio.run, _search()).result()
        else:
            return loop.run_until_complete(_search())
    except RuntimeError:
        return asyncio.run(_search())
```

---

## Usage Examples

### Basic Usage

```python
from services.searxng_rich_search import searxng_client

# General search
response = await searxng_client.search("machine learning tutorials")

# Image search
response = await searxng_client.search_images("cute cats")

# Video search
response = await searxng_client.search_videos("python tutorial")

# News search (last week)
response = await searxng_client.search_news(
    "artificial intelligence",
    time_range=TimeRange.WEEK
)

# Academic search
response = await searxng_client.search_science("quantum computing")

# IT/Programming search
response = await searxng_client.search_it("rust async await")
```

### DSPy ReAct Integration

```python
import dspy
from services.searxng_rich_search import (
    searxng_search_general,
    searxng_search_images,
    searxng_search_videos,
    searxng_search_news,
)

# Initialize ReAct with rich search tools
react = dspy.ReAct(
    "question->answer",
    tools=[
        dspy.Tool(searxng_search_general, name="web_search"),
        dspy.Tool(searxng_search_images, name="image_search"),
        dspy.Tool(searxng_search_videos, name="video_search"),
        dspy.Tool(searxng_search_news, name="news_search"),
    ],
)

# Use the agent
result = react(question="Find recent news about AI and show me some AI-generated images")
```

---

## API Response Examples

### General Search Response

```json
{
  "query": "python async await",
  "number_of_results": 10,
  "results": [
    {
      "url": "https://docs.python.org/3/library/asyncio.html",
      "title": "asyncio — Asynchronous I/O",
      "content": "This module provides the infrastructure for writing single-threaded concurrent code...",
      "engine": "google",
      "category": "general",
      "score": 1.0,
      "engines": ["google", "bing"],
      "positions": [1, 2]
    }
  ],
  "answers": [],
  "corrections": [],
  "suggestions": ["python async await example", "python asyncio tutorial"]
}
```

### Image Search Response

```json
{
  "query": "mountain landscape",
  "number_of_results": 20,
  "results": [
    {
      "url": "https://example.com/image-page",
      "title": "Mountain Landscape",
      "content": "Beautiful mountain landscape at sunset",
      "img_src": "https://example.com/full-image.jpg",
      "thumbnail_src": "https://example.com/thumb.jpg",
      "source": "Unsplash",
      "engine": "google images",
      "category": "images",
      "score": 0.95
    }
  ]
}
```

### News Search Response

```json
{
  "query": "artificial intelligence",
  "number_of_results": 15,
  "results": [
    {
      "url": "https://example.com/news-article",
      "title": "Breakthrough in AI Research",
      "content": "Researchers announce significant advancement...",
      "source": "Tech News",
      "publishedDate": "2025-01-20T10:30:00",
      "engine": "google news",
      "category": "news",
      "score": 0.98
    }
  ]
}
```

---

## Configuration

### SearXNG settings.yml

```yaml
use_default_settings: true
server:
  secret_key: "your-secret-key"
  limiter: false
  image_proxy: true

search:
  formats:
    - html
    - json    # Required for API
    - csv
    - rss
```

### Environment Variables

```bash
# .env file
SEARXNG_URL=http://localhost:8080
SEARXNG_ENGINES=google,bing,duckduckgo,brave
SEARXNG_LANGUAGE=en
SEARXNG_SAFESEARCH=1
```

---

## Best Practices

1. **Set `format=json`** - Always specify JSON format for API responses
2. **Use specific categories** - For better results, specify category (images, videos, news)
3. **Enable image_proxy** - Proxies images through SearXNG for privacy
4. **Handle unresponsive engines** - Check `unresponsive_engines` in response
5. **Use time_range for news** - Filter by day/week/month for recent news
6. **Limit results with page numbers** - Use `pageno` for pagination
7. **Parse answers first** - Check `answers` field for instant facts
8. **Check corrections** - Use `corrections` for spelling suggestions

---

## Troubleshooting

### 403 Forbidden

**Cause**: JSON format not enabled in settings.yml

**Fix**: Add `json` to formats:
```yaml
search:
  formats:
    - html
    - json
```

### No Results

**Cause**: Engine may be blocked or category unavailable

**Fix**: Check `unresponsive_engines` in response, try different engines

### Slow Response

**Cause**: Too many engines or timeout too low

**Fix**: Reduce engines or increase timeout

---

## References

- SearXNG Documentation: https://docs.searxng.org/
- Search API: https://docs.searxng.org/dev/search_api.html
- Settings: https://docs.searxng.org/admin/settings/
- Public Instances: https://searx.space/

---

**Last Updated**: 2026-01-21
