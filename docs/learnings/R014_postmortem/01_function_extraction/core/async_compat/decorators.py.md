# Function Extraction: core/async_compat/decorators.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/core/async_compat/decorators.py`

## File Size
67 lines

## Purpose

    The decorated function can be called from sync or async contexts
    and will automatically adapt based on hardware capabilities.

    Args:
        module_name: Name of module for hardware detec

## Key Classes
- `MyAgent`

## Key Functions
- async `aforward()`
- `auto_async()`
- `decorator()`
- `wrapper()`

## Dependencies
- import asyncio
- import functools
- import logging
- from core.async_compat.hardware_detection import should_use_async

## Data Structures
See key classes above

## Business Logic
This module contains 1 classes and 4 functions.
It focuses on async operations.
Code complexity: 41 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.518028
- Lines of code: 41
