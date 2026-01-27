# Function Extraction: services/master_agent/orchestration/phase_executor.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/master_agent/orchestration/phase_executor.py`

## File Size
80 lines

## Purpose

    def __init__(
        self,
        qa: QACheckpointModule,
        qa_callback: Callable | None = None,
    ) -> None:

## Key Classes
- `PhaseExecutor`

## Key Functions
- `__init__()`
- `execute_phase()`
- `_emit_qa_progress()`

## Dependencies
- import asyncio
- import logging
- from typing import Callable
- from services.master_agent.qa_checkpoints import QACheckpointModule

## Data Structures
See key classes above

## Business Logic
This module contains 1 classes and 3 functions.
It uses synchronous operations.
Code complexity: 61 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.527706
- Lines of code: 61
