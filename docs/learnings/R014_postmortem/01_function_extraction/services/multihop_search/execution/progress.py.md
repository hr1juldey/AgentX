# Function Extraction: services/multihop_search/execution/progress.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/multihop_search/execution/progress.py`

## File Size
136 lines

## Purpose

    def __init__(
        self,
        progress_callback: Any,
        max_hops: int,
    ):

## Key Classes
- `HopProgressTracker`

## Key Functions
- `__init__()`
- `send_hop_start()`
- `send_documents_found()`
- `send_assessing()`
- `send_complete()`
- `_send_progress_event()`

## Dependencies
- from typing import Any
- from services.multihop_search.execution.hop_helpers import send_progress_event

## Data Structures
See key classes above

## Business Logic
This module contains 1 classes and 6 functions.
It uses synchronous operations.
Code complexity: 114 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.533918
- Lines of code: 114
