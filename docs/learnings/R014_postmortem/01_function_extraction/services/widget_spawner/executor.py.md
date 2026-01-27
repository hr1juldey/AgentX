# Function Extraction: services/widget_spawner/executor.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/widget_spawner/executor.py`

## File Size
143 lines

## Purpose

    This agent focuses ONLY on execution:
    - Takes a plan from the planner
    - Generates each widget with its specific context
    - Returns the complete list of generated widgets

    It does N

## Key Classes
- `WidgetExecutorAgent`

## Key Functions
- `__init__()`
- `execute_plan()`
- `_generate_widget()`

## Dependencies
- import logging
- import uuid
- import dspy
- from services.tools.researcher.searxng_search import SearXNGSearchModule
- from services.widget_spawner.builders import (
- from services.widget_spawner.executor_helpers import (
- from services.widget_spawner.models import WidgetDescriptor
- from services.widget_spawner.signatures import (

## Data Structures
See key classes above

## Business Logic
This module contains 1 classes and 3 functions.
It uses synchronous operations.
Code complexity: 98 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.563712
- Lines of code: 98
