# Function Extraction: services/pipeline/researcher_process.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/pipeline/researcher_process.py`

## File Size
127 lines

## Purpose

    Args:
        raw_data: List of search result dicts with 'url' field
        max_fetch: Maximum number of pages to fetch (to limit latency)

    Returns:
        Enriched raw_data with 'full_cont

## Key Classes
None

## Key Functions
- `enrich_raw_data_with_content()`
- `process_research_data()`

## Dependencies
- import asyncio
- import logging
- from concurrent.futures import ThreadPoolExecutor
- from typing import Any, cast
- from services.tools.researcher.number_extractor import NumberExtractorModule
- from services.tools.researcher.web_fetcher import fetch_multiple_pages

## Data Structures
See key classes above

## Business Logic
This module contains 0 classes and 2 functions.
It uses synchronous operations.
Code complexity: 84 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.542252
- Lines of code: 84
