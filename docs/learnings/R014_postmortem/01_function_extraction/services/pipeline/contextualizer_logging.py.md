# Function Extraction: services/pipeline/contextualizer_logging.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/pipeline/contextualizer_logging.py`

## File Size
98 lines

## Purpose

    Args:
        ranked_result: Result from reranker
        raw_data: Original raw data list

    Returns:
        Dictionary with rerank metrics

## Key Classes
None

## Key Functions
- `extract_rerank_metrics()`
- `extract_filter_metrics()`
- `extract_contextualize_metrics()`
- `log_rerank_result()`
- `log_filter_result()`
- `log_contextualize_result()`

## Dependencies
- from services.pipeline.agent_logging import log_step_result, safe_get, safe_get_list

## Data Structures
See key classes above

## Business Logic
This module contains 0 classes and 6 functions.
It uses synchronous operations.
Code complexity: 70 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.537358
- Lines of code: 70
