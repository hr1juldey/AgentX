# Function Extraction: services/pipeline/presenter_modules/progress.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/pipeline/presenter_modules/progress.py`

## File Size
45 lines

## Purpose

    _progress_map = {
        "checking": 33.0,
        "polishing": 66.0,
        "finalizing": 100.0,
    }

    @classmethod
    def get_progress_status(cls, phase: str = "polishing") -> dict:

## Key Classes
- `PresenterProgressTracker`

## Key Functions
- `get_progress_status()`
- `get_phase_progress()`

## Dependencies
None

## Data Structures
See key classes above

## Business Logic
This module contains 1 classes and 2 functions.
It uses synchronous operations.
Code complexity: 30 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.541005
- Lines of code: 30
