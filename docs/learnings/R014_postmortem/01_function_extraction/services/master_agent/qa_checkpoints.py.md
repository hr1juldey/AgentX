# Function Extraction: services/master_agent/qa_checkpoints.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/master_agent/qa_checkpoints.py`

## File Size
140 lines

## Purpose

    name: str
    description: str
    passed: bool = False
    checklist: dict = field(default_factory=dict)
    error_message: Optional[str] = None


@dataclass
class QAReport:

## Key Classes
- `QACheckpoint`
- `QAReport`
- `QACheckpointModule`

## Key Functions
- `add_checkpoint()`
- `mark_passed()`
- `mark_failed()`
- `finalize()`
- `__init__()`
- `mark_failed()`
- `validate_checkpoint()`
- `get_checklist_for_ui()`
- `finalize_report()`

## Dependencies
- from typing import Callable, Optional
- from dataclasses import dataclass, field

## Data Structures
See key classes above

## Business Logic
This module contains 3 classes and 9 functions.
It uses synchronous operations.
Code complexity: 112 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.528973
- Lines of code: 112
