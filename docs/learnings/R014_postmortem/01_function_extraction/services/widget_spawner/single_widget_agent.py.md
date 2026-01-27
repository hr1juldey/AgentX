# Function Extraction: services/widget_spawner/single_widget_agent.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/widget_spawner/single_widget_agent.py`

## File Size
107 lines

## Purpose

    This is used when you want to force a single widget type
    or as a simpler fallback when multi-widget is not needed.

## Key Classes
- `SingleWidgetSpawnerAgent`

## Key Functions
- `__init__()`
- `forward()`

## Dependencies
- import uuid
- import dspy
- from services.widget_spawner.builders import (
- from services.widget_spawner.config import AVAILABLE_WIDGET_TYPES
- from services.widget_spawner.models import WidgetDescriptor
- from services.widget_spawner.signatures import (

## Data Structures
See key classes above

## Business Logic
This module contains 1 classes and 2 functions.
It uses synchronous operations.
Code complexity: 77 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.568972
- Lines of code: 77
