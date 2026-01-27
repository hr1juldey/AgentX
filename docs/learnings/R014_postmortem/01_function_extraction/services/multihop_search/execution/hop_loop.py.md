# Function Extraction: services/multihop_search/execution/hop_loop.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/multihop_search/execution/hop_loop.py`

## File Size
123 lines

## Purpose

    SRP: Execute one hop iteration only.

## Key Classes
- `HopLoopExecutor`

## Key Functions
- async `execute_hop_iteration()`
- `__init__()`

## Dependencies
- from __future__ import annotations
- import logging
- from typing import TYPE_CHECKING, Any
- import dspy
- from services.multihop_search.execution.hop_helpers import generate_hop_answer
- from services.multihop_search.execution.progress import HopProgressTracker
- from services.multihop_search.execution.hop_assessment import HopAssessment
- from services.multihop_search.execution.hop_planning import HopPlanning
- from services.multihop_search.execution.hop_search import HopSearch

## Data Structures
See key classes above

## Business Logic
This module contains 1 classes and 2 functions.
It focuses on async operations.
Code complexity: 89 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.532889
- Lines of code: 89
