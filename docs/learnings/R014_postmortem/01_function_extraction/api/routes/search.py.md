# Function Extraction: api/routes/search.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/api/routes/search.py`

## File Size
107 lines

## Purpose
    query = request.get("query", "")

    logger.info(f"🔍 /search called: query='{query[:50]}...'")

    try:
        use_case = get_search_use_case()
        dto_request = SearchRequest(query=query)


## Key Classes
None

## Key Functions
- async `search_endpoint()`
- async `search_websocket()`
- async `send_progress()`

## Dependencies
- import logging
- import uuid
- from typing import Any
- from fastapi import APIRouter, WebSocket, WebSocketDisconnect
- from application.dtos.requests import SearchRequest
- from application.use_cases.search import (

## Data Structures
See key classes above

## Business Logic
This module contains 0 classes and 3 functions.
It focuses on async operations.
Code complexity: 84 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.513715
- Lines of code: 84
