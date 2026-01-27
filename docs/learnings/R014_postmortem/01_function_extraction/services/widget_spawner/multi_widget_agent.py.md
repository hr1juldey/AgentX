# Function Extraction: services/widget_spawner/multi_widget_agent.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/widget_spawner/multi_widget_agent.py`

## File Size
98 lines

## Purpose

    This agent uses ReAct reasoning to:
    1. Analyze the user's request
    2. Decide which widgets are needed (can be multiple)
    3. Call the appropriate widget generation tools
    4. Return a 

## Key Classes
- `MultiWidgetSpawnerAgent`

## Key Functions
- `__init__()`
- `forward()`

## Dependencies
- import json
- import dspy
- from services.widget_spawner.models import WidgetDescriptor
- from services.widget_spawner.tools import WIDGET_TOOLS

## Data Structures
See key classes above

## Business Logic
This module contains 1 classes and 2 functions.
It uses synchronous operations.
Code complexity: 63 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.565958
- Lines of code: 63
