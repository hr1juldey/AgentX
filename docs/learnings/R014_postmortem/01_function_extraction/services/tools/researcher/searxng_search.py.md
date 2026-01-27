# Function Extraction: services/tools/researcher/searxng_search.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/tools/researcher/searxng_search.py`

## File Size
148 lines

## Purpose

    Has 3 signatures:
    - SearchGeneral: General web search
    - SearchImages: Image search
    - SearchNews: News search

## Key Classes
- `SearXNGSearchModule`

## Key Functions
- async `_search_with_engines()`
- async `_search_searxng()`
- `__init__()`
- `forward()`

## Dependencies
- import asyncio
- import logging
- from typing import Optional
- import dspy
- import httpx
- from services.tools.researcher.search_async_wrapper import run_async_in_sync_context
- from services.tools.researcher.search_domain_priority import (
- from services.tools.researcher.search_result_processor import extract_url_list

## Data Structures
See key classes above

## Business Logic
This module contains 1 classes and 4 functions.
It focuses on async operations.
Code complexity: 105 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.558904
- Lines of code: 105
