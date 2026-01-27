# Function Extraction: services/tools/researcher/web_fetcher.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/tools/researcher/web_fetcher.py`

## File Size
140 lines

## Purpose

    Args:
        url: URL to fetch
        timeout: Request timeout in seconds

    Returns:
        Dict with url, title, markdown_content, links (list of dicts)
        or None if fetch fails

## Key Classes
None

## Key Functions
- async `fetch_page()`
- async `fetch_multiple_pages()`
- `truncate_content()`

## Dependencies
- import asyncio
- import logging
- from typing import Optional
- import httpx
- from bs4 import BeautifulSoup
- import html2text

## Data Structures
See key classes above

## Business Logic
This module contains 0 classes and 3 functions.
It focuses on async operations.
Code complexity: 94 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.559279
- Lines of code: 94
