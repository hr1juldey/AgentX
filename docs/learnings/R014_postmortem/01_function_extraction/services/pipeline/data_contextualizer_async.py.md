# Function Extraction: services/pipeline/data_contextualizer_async.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/pipeline/data_contextualizer_async.py`

## File Size
102 lines

## Purpose

    Uses async for reranking, filtering, and contextualization steps to achieve
    ~4x speedup with 4 concurrent LLM calls per step.

    Args:
        agent: DataContextualizerAgent instance with r

## Key Classes
None

## Key Functions
- async `async_contextualize_forward()`

## Dependencies
- import logging
- import time
- from services.pipeline.contextualizer_logging import (
- from services.pipeline.data_contextualizer_builder import (
- from services.pipeline.data_contextualizer_utils import extract_top_facts

## Data Structures
See key classes above

## Business Logic
This module contains 0 classes and 1 functions.
It focuses on async operations.
Code complexity: 80 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.538510
- Lines of code: 80
