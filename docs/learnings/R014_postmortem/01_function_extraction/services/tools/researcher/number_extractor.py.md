# Function Extraction: services/tools/researcher/number_extractor.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/tools/researcher/number_extractor.py`

## File Size
110 lines

## Purpose

    Processes raw research documents and extracts numerical data
    with labels, values, units, and source citations.

## Key Classes
- `NumberExtractorModule`

## Key Functions
- `__init__()`
- `forward()`
- `_deduplicate()`

## Dependencies
- from typing import Any
- import logging
- import dspy
- from services.tools.hydrators.chart_signatures import ExtractDocumentNumbers
- from services.tools.researcher.llm_number_handler import (
- from services.tools.researcher.regex_fallback import extract_numbers_with_regex

## Data Structures
See key classes above

## Business Logic
This module contains 1 classes and 3 functions.
It uses synchronous operations.
Code complexity: 78 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.557292
- Lines of code: 78
