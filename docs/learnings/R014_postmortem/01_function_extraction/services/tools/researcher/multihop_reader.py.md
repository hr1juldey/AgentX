# Function Extraction: services/tools/researcher/multihop_reader.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/tools/researcher/multihop_reader.py`

## File Size
145 lines

## Purpose

    Two modes:
    1. Basic: Single URL → extract relevant content + generate report
    2. Multi-hop: Multiple URLs → recursive link following → n² reports

    n² formula: Total reports = n² where 

## Key Classes
- `MultiHopReader`

## Key Functions
- async `basic_read()`
- async `multihop_read()`
- `__init__()`

## Dependencies
- import logging
- from services.tools.researcher.content_filter import ContentFilterModule
- from services.tools.researcher.multihop_basic import basic_read
- from services.tools.researcher.multihop_processor import (
- from services.tools.researcher.report_generator import ReportGeneratorModule

## Data Structures
See key classes above

## Business Logic
This module contains 1 classes and 3 functions.
It focuses on async operations.
Code complexity: 107 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.557016
- Lines of code: 107
