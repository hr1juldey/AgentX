# Function Extraction: services/multihop_search/agents/multihop_agent.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/multihop_search/agents/multihop_agent.py`

## File Size
75 lines

## Purpose

    Automatically detects GPU capabilities and uses optimal execution strategy:
    - RTX 3060: Sequential execution
    - DGX Pro: Parallel I/O operations

    Orchestrates domain logic through HopO

## Key Classes
- `MultiHopSearchAgent`

## Key Functions
- `__init__()`

## Dependencies
- from __future__ import annotations
- import logging
- from typing import Any, Callable
- import dspy
- from services.multihop_search.agents.async_execution import AsyncExecutionMixin
- from services.multihop_search.agents.async_forward import AsyncForwardMixin
- from services.multihop_search.agents.sync_forward import SyncForwardMixin
- from services.multihop_search.execution.hop_orchestrator import HopOrchestrator
- from services.multihop_search.reflection import CompletenessAssessor, HopPlanner
- from services.multihop_search.search_client import get_search_client
- from services.multihop_search.signatures import SynthesizeFinalAnswer
- from services.multihop_search.time_estimator import get_time_estimator

## Data Structures
See key classes above

## Business Logic
This module contains 1 classes and 1 functions.
It uses synchronous operations.
Code complexity: 55 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.531708
- Lines of code: 55
