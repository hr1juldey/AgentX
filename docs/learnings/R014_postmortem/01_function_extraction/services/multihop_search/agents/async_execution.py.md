# Function Extraction: services/multihop_search/agents/async_execution.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/multihop_search/agents/async_execution.py`

## File Size
74 lines

## Purpose

    def _init_executor(self, module_name: str) -> SafeAsyncExecutor:

## Key Classes
- `AsyncExecutionMixin`

## Key Functions
- `_init_executor()`
- `_execute_hops_sync()`
- `_send_progress()`

## Dependencies
- import asyncio
- import logging
- from core.async_compat import SafeAsyncExecutor
- from services.multihop_search.schemas import HopEvent

## Data Structures
See key classes above

## Business Logic
This module contains 1 classes and 3 functions.
It uses synchronous operations.
Code complexity: 53 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.531254
- Lines of code: 53
