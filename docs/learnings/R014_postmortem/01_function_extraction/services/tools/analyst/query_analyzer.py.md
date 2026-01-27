# Function Extraction: services/tools/analyst/query_analyzer.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/tools/analyst/query_analyzer.py`

## File Size
100 lines

## Purpose

    def __init__(self):
        super().__init__()
        self.detect_type = dspy.Predict("query -> query_type")
        self.extract_domain = dspy.Predict("query -> domain")
        self.identify_u

## Key Classes
- `ContextAnalyzerModule`
- `InsightExtractorModule`

## Key Functions
- `__init__()`
- `forward()`
- `__init__()`
- `forward()`
- `_extract_single()`
- `_extract_iterative()`
- `_parse_insights()`

## Dependencies
- import dspy
- from typing import List
- from services.tools.analyst.signatures import (
- from services.core.chunking import chunk_text, deduplicate_items

## Data Structures
See key classes above

## Business Logic
This module contains 2 classes and 7 functions.
It uses synchronous operations.
Code complexity: 71 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.545031
- Lines of code: 71
