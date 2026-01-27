# Function Extraction: services/multihop_search/execution/hop_planning.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/multihop_search/execution/hop_planning.py`

## File Size
127 lines

## Purpose

    SRP: Plan next hop only.

## Key Classes
- `HopPlanning`

## Key Functions
- async `plan_next()`
- `__init__()`
- `_send_progress()`

## Dependencies
- from __future__ import annotations
- import logging
- from typing import TYPE_CHECKING, Any
- import dspy
- from services.multihop_search.reflection import HopPlanner
- from services.multihop_search.execution.hop_helpers import send_progress_event

## Data Structures
See key classes above

## Business Logic
This module contains 1 classes and 3 functions.
It focuses on async operations.
Code complexity: 98 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.533395
- Lines of code: 98
