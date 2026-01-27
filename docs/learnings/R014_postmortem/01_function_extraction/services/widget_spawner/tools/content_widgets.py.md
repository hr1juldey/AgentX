# Function Extraction: services/widget_spawner/tools/content_widgets.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/widget_spawner/tools/content_widgets.py`

## File Size
113 lines

## Purpose
    return str(uuid.uuid4())


def create_markdown_widget(query: str, context: str = "") -> str:

## Key Classes
None

## Key Functions
- `_generate_widget_id()`
- `create_markdown_widget()`
- `create_card_widget()`
- `create_form_widget()`
- `create_progress_widget()`
- `create_chart_widget()`

## Dependencies
- import json
- import uuid
- import dspy
- from services.widget_spawner.builders import (
- from services.widget_spawner.signatures import (

## Data Structures
See key classes above

## Business Logic
This module contains 0 classes and 6 functions.
It uses synchronous operations.
Code complexity: 80 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.569489
- Lines of code: 80
