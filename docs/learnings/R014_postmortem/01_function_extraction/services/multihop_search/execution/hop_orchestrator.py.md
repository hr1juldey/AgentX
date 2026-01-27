# Function Extraction: services/multihop_search/execution/hop_orchestrator.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/multihop_search/execution/hop_orchestrator.py`

## File Size
100 lines

## Purpose

    Delegates to specialized modules for SRP compliance.

## Key Classes
- `HopOrchestrator`

## Key Functions
- async `execute_hops()`
- `__init__()`

## Dependencies
- from __future__ import annotations
- import logging
- from typing import TYPE_CHECKING, Any
- import dspy
- from services.multihop_search.execution.hop_assessment import HopAssessment
- from services.multihop_search.execution.hop_loop import HopLoopExecutor
- from services.multihop_search.execution.hop_planning import HopPlanning
- from services.multihop_search.execution.hop_search import HopSearch

## Data Structures
See key classes above

## Business Logic
This module contains 1 classes and 2 functions.
It focuses on async operations.
Code complexity: 72 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.533135
- Lines of code: 72
