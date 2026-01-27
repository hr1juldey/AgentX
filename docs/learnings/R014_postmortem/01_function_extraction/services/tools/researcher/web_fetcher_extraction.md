# Function Postmortem: services/tools/researcher/web_fetcher.py

## Metadata
- **File**: services/tools/researcher/web_fetcher.py
- **Lines of Code**: 140
- **Purpose**: Web fetching service (not DSPy module)
- **Dependencies**: `httpx`, `BeautifulSoup`, `html2text`

---

## Analysis

**File Status**: PRODUCTION SERVICE LAYER

**Purpose**: Pure service for fetching and parsing web pages. Not a DSPy module - uses httpx, BeautifulSoup, html2text.

---

## Functions Extracted

### fetch_page

**Purpose**: Fetch a single web page and convert to markdown

**Signature**:
```python
async def fetch_page(url: str, timeout: float = 15.0) -> Optional[dict]:
```

**Lines**: 25-89

**Complexity**: O(n) where n is page size

**Key Code**:
```python
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
```

**What Works**:
- ✅ Async httpx for non-blocking requests
- ✅ follow_redirects=True for URL shorteners
- ✅ Custom User-Agent header
- ✅ BeautifulSoup for HTML parsing
- ✅ Removes script/style/nav/footer/header (clean content)
- ✅ html2text for markdown conversion
- ✅ Handles None from soup.title.string properly
- ✅ Limits links to 50 (avoids bloat)
- ✅ Only includes HTTP(S) links (skips mailto:, javascript:)
- ✅ Exception handling with None return
- ✅ Type hints with Optional

**Mistakes Found**: None

**Behavioral Notes**:
- Timeout default 15 seconds
- Removes nav/footer/header (keeps main content)
- Truncates link text to 100 chars
- Returns None on any exception (logged)
- Body width unlimited (H2T.body_width = 0)

**Dependencies**:
- **Imports**: httpx, BeautifulSoup, html2text
- **Called by**: fetch_multiple_pages, researcher tools
- **Returns**: Dict with url, title, markdown_content, links or None

**Reusability**: HIGH - Standard web fetching pattern

---

### fetch_multiple_pages

**Purpose**: Fetch multiple pages concurrently

**Signature**:
```python
async def fetch_multiple_pages(urls: list[str]) -> list[dict]:
```

**Lines**: 91-113

**Complexity**: O(n) where n is number of URLs (parallel)

**Key Code**:
```python
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
```

**What Works**:
- ✅ asyncio.gather for concurrent execution
- ✅ return_exceptions=True (doesn't raise on individual failures)
- ✅ Filters out exceptions and None values
- ✅ Logs success ratio (X/Y pages successfully)
- ✅ List comprehension for task creation
- ✅ Type hints with list[str]

**Mistakes Found**: None

**Behavioral Notes**:
- All fetches run in parallel (not sequential)
- Failed fetches are silently skipped (logged)
- Returns only successful pages
- Partial success possible (e.g., 3/5 pages)

**Dependencies**:
- **Imports**: asyncio
- **Calls**: fetch_page
- **Returns**: List of successful page dicts

**Reusability**: HIGH - Standard concurrent fetching pattern

---

### truncate_content

**Purpose**: Truncate content to max characters, preserving sentence boundaries

**Signature**:
```python
def truncate_content(content: str, max_chars: int = 2000) -> str:
```

**Lines**: 116-140

**Complexity**: O(n) where n is content length

**Key Code**:
```python
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
```

**What Works**:
- ✅ Preserves sentence boundaries (period or newline)
- ✅ Uses later boundary (max of period/newline)
- ✅ Safety check: keeps at least half content
- ✅ Adds "..." if no good boundary found
- ✅ Early return if no truncation needed
- ✅ Type hints with defaults

**Mistakes Found**: None

**Behavioral Notes**:
- Default max 2000 characters
- Prefers period over newline (both equal, max picks later)
- Only truncates at boundary if > half content
- Otherwise hard truncation with "..."

**Dependencies**:
- **Imports**: None (pure function)
- **Called by**: Researcher tools, content processors

**Reusability**: HIGH - Smart truncation pattern

---

## Module Variables

### H2T

**Purpose**: Global html2text converter configuration

**Lines**: 17-22

**Key Code**:
```python
# Configure html2text for markdown conversion
H2T = html2text.HTML2Text()
H2T.ignore_links = False
H2T.ignore_images = False
H2T.body_width = 0  # Don't wrap lines
H2T.unicode_snob = True
```

**What Works**:
- ✅ Keeps links (ignore_links=False)
- ✅ Keeps images (ignore_images=False)
- ✅ No line wrapping (body_width=0)
- ✅ Unicode support (unicode_snob=True)

**Reusability**: HIGH - Standard html2text config

---

## File Summary

**Total Functions**: 3
**Lines of Code**: 140

**Violations**: None

**Success Patterns**:
- ✅ **Async Fetching**: httpx.AsyncClient with follow_redirects
- ✅ **BeautifulSoup Parsing**: Remove nav/footer/header
- ✅ **html2text Conversion**: Clean markdown output
- ✅ **Concurrent Execution**: asyncio.gather for multiple URLs
- ✅ **Smart Truncation**: Preserves sentence boundaries
- ✅ **Type Hints**: Optional[dict], list[str]
- ✅ **Exception Handling**: None return on failure

**Overall Assessment**: EXCELLENT - Clean web fetching service.

**Key Learnings for Real AgentX**:
1. ✅ **Async httpx**: Use httpx.AsyncClient, not requests
2. ✅ **follow_redirects=True**: Handle URL shorteners
3. ✅ **Remove Noise**: Strip nav/footer/header/scripts
4. ✅ **html2text Config**: body_width=0 for no wrapping
5. ✅ **Concurrent Fetch**: asyncio.gather for parallel
6. ✅ **Smart Truncate**: Preserve sentence boundaries

**Reuse for Real AgentX**: ✅ HIGH - Copy entire file for web fetching.
