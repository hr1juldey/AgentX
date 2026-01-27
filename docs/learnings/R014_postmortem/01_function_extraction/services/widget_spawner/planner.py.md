# Function Extraction: services/widget_spawner/planner.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/widget_spawner/planner.py`

## File Size
124 lines

## Purpose

    This planner analyzes the user's request and decides:
    1. What widget types are needed
    2. In what order
    3. With what context/instructions for each

    Widget Selection Guide:
    - "m

## Key Classes
- `PlanWidgetsSignature`
- `WidgetPlannerAgent`

## Key Functions
- `__init__()`
- `forward()`

## Dependencies
- import json
- import logging
- import dspy
- from services.widget_spawner.config import AVAILABLE_WIDGET_TYPES

## Data Structures
See key classes above

## Business Logic
This module contains 2 classes and 2 functions.
It uses synchronous operations.
Code complexity: 86 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.566246
- Lines of code: 86
