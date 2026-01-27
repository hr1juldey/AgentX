# Function Extraction: services/multihop_search/signatures.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/multihop_search/signatures.py`

## File Size
92 lines

## Purpose

    The first hop should use the original question directly.
    Subsequent hops should refine the query based on what we've learned.

## Key Classes
- `GenerateSearchQuery`
- `AnswerWithSources`
- `CheckCompleteness`
- `GenerateNextQuery`
- `SynthesizeFinalAnswer`

## Key Functions
None

## Dependencies
- from __future__ import annotations
- import dspy
- from dspy.signatures import Signature

## Data Structures
See key classes above

## Business Logic
This module contains 5 classes and 0 functions.
It uses synchronous operations.
Code complexity: 60 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.535494
- Lines of code: 60
