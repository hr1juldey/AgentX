# Function Extraction: services/widget_spawner/service.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/widget_spawner/service.py`

## File Size
101 lines

## Purpose

    Architecture:
    1. WidgetPlannerAgent - Decides WHAT widgets to spawn
    2. WidgetExecutorAgent - Actually SPAWNS the widgets

    This provides clean separation of concerns:
    - Planner: De

## Key Classes
- `WidgetSpawnerService`

## Key Functions
- async `generate_widget()`
- `__init__()`
- `_ensure_configured()`
- `get_widget_spawner_service()`

## Dependencies
- from services.widget_spawner.executor import WidgetExecutorAgent
- from services.widget_spawner.models import MultiWidgetGenerationResponse
- from services.widget_spawner.planner import WidgetPlannerAgent

## Data Structures
See key classes above

## Business Logic
This module contains 1 classes and 4 functions.
It focuses on async operations.
Code complexity: 65 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.568413
- Lines of code: 65
