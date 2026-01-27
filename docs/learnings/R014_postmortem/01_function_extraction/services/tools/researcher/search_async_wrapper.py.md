# Function Extraction: services/tools/researcher/search_async_wrapper.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/tools/researcher/search_async_wrapper.py`

## File Size
33 lines

## Purpose

    Detects if an event loop is already running and creates a new thread
    with its own loop if needed. This allows async code to work from
    sync contexts without conflicts.

    Args:
        c

## Key Classes
None

## Key Functions
- `run_async_in_sync_context()`

## Dependencies
- import asyncio
- from concurrent.futures import ThreadPoolExecutor
- from typing import Any, Coroutine

## Data Structures
See key classes above

## Business Logic
This module contains 0 classes and 1 functions.
It uses synchronous operations.
Code complexity: 20 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.558180
- Lines of code: 20
