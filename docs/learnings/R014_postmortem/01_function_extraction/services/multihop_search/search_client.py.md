# Function Extraction: services/multihop_search/search_client.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/multihop_search/search_client.py`

## File Size
119 lines

## Purpose

    url: str
    title: str
    content: str
    engine: str
    score: float
    category: str = "general"


class SearXNGClient:

## Key Classes
- `SearchResultItem`
- `SearXNGClient`

## Key Functions
- async `search()`
- `__init__()`
- `get_search_client()`

## Dependencies
- from __future__ import annotations
- import logging
- from dataclasses import dataclass
- import httpx

## Data Structures
See key classes above

## Business Logic
This module contains 2 classes and 3 functions.
It focuses on async operations.
Code complexity: 86 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.535257
- Lines of code: 86
