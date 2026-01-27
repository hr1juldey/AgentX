# Function Extraction: services/tools/contextualizer/reranker.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/tools/contextualizer/reranker.py`

## File Size
87 lines

## Purpose

    Has 2 signatures:
    - ScoreRelevance: Score each result's relevance to query (returns float)
    - RankByQuality: Rank results by quality score

## Key Classes
- `RerankerModule`

## Key Functions
- async `aforward()`
- async `score_result()`
- `__init__()`
- `forward()`

## Dependencies
- import asyncio
- import dspy
- from config.settings import settings
- from services.tools.common.type_utils import _to_float
- from services.tools.contextualizer.async_executor import execute_parallel
- from services.tools.contextualizer.signatures import ScoreRelevanceSignature

## Data Structures
See key classes above

## Business Logic
This module contains 1 classes and 4 functions.
It focuses on async operations.
Code complexity: 59 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.548177
- Lines of code: 59
