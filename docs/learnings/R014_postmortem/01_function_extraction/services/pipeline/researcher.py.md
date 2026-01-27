# Function Extraction: services/pipeline/researcher.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/pipeline/researcher.py`

## File Size
101 lines

## Purpose

    Uses SearXNG to fetch live web data and processes it for presentation.

## Key Classes
- `ResearcherAgent`

## Key Functions
- `__init__()`
- `forward()`

## Dependencies
- import logging
- from typing import Optional
- import dspy
- from services.pipeline.researcher_filter import (
- from services.pipeline.researcher_process import process_research_data
- from services.pipeline.researcher_result import build_researcher_result
- from services.pipeline.researcher_search import (
- from services.tools.researcher import (

## Data Structures
See key classes above

## Business Logic
This module contains 1 classes and 2 functions.
It uses synchronous operations.
Code complexity: 77 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.541500
- Lines of code: 77
