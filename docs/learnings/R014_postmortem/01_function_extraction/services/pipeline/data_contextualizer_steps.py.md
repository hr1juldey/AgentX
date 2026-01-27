# Function Extraction: services/pipeline/data_contextualizer_steps.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/pipeline/data_contextualizer_steps.py`

## File Size
135 lines

## Purpose

Extracts the three main steps (rerank, filter, contextualize) into
separate functions for better modularity.

## Key Classes
None

## Key Functions
- `execute_rerank_step()`
- `execute_filter_step()`
- `execute_contextualize_step()`

## Dependencies
- import logging
- import time
- from services.pipeline.contextualizer_logging import (
- from services.pipeline.contextualizer_tracking_steps import (
- from services.pipeline.data_contextualizer_utils import extract_top_facts

## Data Structures
See key classes above

## Business Logic
This module contains 0 classes and 3 functions.
It uses synchronous operations.
Code complexity: 111 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.538989
- Lines of code: 111
