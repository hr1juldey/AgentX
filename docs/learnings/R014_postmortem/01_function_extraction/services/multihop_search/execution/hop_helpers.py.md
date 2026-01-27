# Function Extraction: services/multihop_search/execution/hop_helpers.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/multihop_search/execution/hop_helpers.py`

## File Size
115 lines

## Purpose
    if callback is None:
        return

    from services.multihop_search.schemas import HopEvent

    event = HopEvent(
        event_type=event_type,
        hop_number=hop_number,
        total_ho

## Key Classes
None

## Key Functions
- `send_progress_event()`
- `summarize_documents()`
- `build_search_context()`
- `generate_search_query()`
- `generate_hop_answer()`

## Dependencies
- from __future__ import annotations
- from typing import Any
- import dspy
- from services.multihop_search.search_client import SearchResultItem
- from services.multihop_search.schemas import HopEvent

## Data Structures
See key classes above

## Business Logic
This module contains 0 classes and 5 functions.
It uses synchronous operations.
Code complexity: 87 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.532624
- Lines of code: 87
