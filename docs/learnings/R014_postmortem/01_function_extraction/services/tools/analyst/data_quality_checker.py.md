# Function Extraction: services/tools/analyst/data_quality_checker.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/tools/analyst/data_quality_checker.py`

## File Size
64 lines

## Purpose

    Has 3 signatures:
    - AssessCompleteness: Assess if data is complete (returns float)
    - AssessRelevance: Assess if data is relevant to query (returns float)
    - DecideResearch: Decide if m

## Key Classes
- `DataQualityCheckerModule`

## Key Functions
- `__init__()`
- `forward()`

## Dependencies
- import dspy
- from services.tools.analyst.signatures import (
- from services.tools.common.type_utils import _to_bool, _to_float

## Data Structures
See key classes above

## Business Logic
This module contains 1 classes and 2 functions.
It uses synchronous operations.
Code complexity: 44 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.544559
- Lines of code: 44
