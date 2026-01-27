# Function Extraction: services/pipeline/analyst.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/pipeline/analyst.py`

## File Size
80 lines

## Purpose

    Runs twice in the pipeline:
    - Pass 1: Understand query and context (before research)
    - Pass 2: Judge data quality and completeness (after contextualization)

## Key Classes
- `AnalystAgent`

## Key Functions
- `__init__()`
- `forward()`

## Dependencies
- from typing import Optional
- import dspy
- from services.pipeline.analyst_modules.data_judgment import DataJudgmentHandler
- from services.pipeline.analyst_modules.initial_analysis import InitialAnalysisHandler
- from services.tools.analyst import (

## Data Structures
See key classes above

## Business Logic
This module contains 1 classes and 2 functions.
It uses synchronous operations.
Code complexity: 57 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.536403
- Lines of code: 57
