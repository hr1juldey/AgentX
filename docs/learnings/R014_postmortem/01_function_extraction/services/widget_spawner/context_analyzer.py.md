# Function Extraction: services/widget_spawner/context_analyzer.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/widget_spawner/context_analyzer.py`

## File Size
141 lines

## Purpose
    query_lower = query.lower()

    if any(
        kw in query_lower
        for kw in [
            "data",
            "trends",
            "sales",
            "chart",
            "graph",
    

## Key Classes
- `AnalyzeContextSignature`
- `ContextAnalyzerAgent`

## Key Functions
- `detect_content_type()`
- `infer_user_goal()`
- `check_device_capabilities()`
- `__init__()`
- `forward()`

## Dependencies
- import json
- import logging
- from typing import Dict, Any
- import dspy

## Data Structures
See key classes above

## Business Logic
This module contains 2 classes and 5 functions.
It uses synchronous operations.
Code complexity: 107 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.563001
- Lines of code: 107
