# Function Extraction: application/use_cases/search.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/application/use_cases/search.py`

## File Size
103 lines

## Purpose

    This is a facade that wraps the existing MultiHopSearchAgent
    to provide a clean architectural boundary.

    Phase 1: Thin wrapper - no behavior changes, just delegates to service.
    Phase 

## Key Classes
- `SearchUseCase`
- `MultiHopSearchWebSocketUseCase`

## Key Functions
- async `search()`
- async `search_with_streaming()`
- `get_search_use_case()`
- `get_websocket_search_use_case()`

## Dependencies
- from collections.abc import Callable
- from typing import Any
- from application.dtos.requests import SearchRequest
- from application.dtos.responses import SearchResultResponse
- from config.settings import settings
- from services.multihop_search.agents import MultiHopSearchAgent
- from services.multihop_search.agents import MultiHopSearchAgent

## Data Structures
See key classes above

## Business Logic
This module contains 2 classes and 4 functions.
It focuses on async operations.
Code complexity: 70 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.516562
- Lines of code: 70
