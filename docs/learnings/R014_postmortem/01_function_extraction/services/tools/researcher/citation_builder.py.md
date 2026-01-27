# Function Extraction: services/tools/researcher/citation_builder.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/tools/researcher/citation_builder.py`

## File Size
108 lines

## Purpose

    sentence: str = dspy.InputField(desc="Sentence to evaluate")
    source_info: str = dspy.InputField(desc="Source: Title | URL")
    relevance_score: str = dspy.OutputField(
        desc="Relevanc

## Key Classes
- `FindBestCitationSpot`
- `CitationBuilderModule`

## Key Functions
- `__init__()`
- `_parse_relevance_score()`
- `forward()`

## Dependencies
- import dspy
- import re

## Data Structures
See key classes above

## Business Logic
This module contains 2 classes and 3 functions.
It uses synchronous operations.
Code complexity: 72 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.554888
- Lines of code: 72
