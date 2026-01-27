# Function Extraction: services/widget_spawner/models.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/widget_spawner/models.py`

## File Size
43 lines

## Purpose

    prompt: str
    widget_type: str | None = None


class MultiWidgetGenerationResponse(BaseModel):

## Key Classes
- `WidgetGenerationRequest`
- `MultiWidgetGenerationResponse`

## Key Functions
None

## Dependencies
- from typing import Any
- from pydantic import BaseModel
- from domain.entities.ui_descriptor import UIDescriptor

## Data Structures
See key classes above

## Business Logic
This module contains 2 classes and 0 functions.
It uses synchronous operations.
Code complexity: 16 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.565702
- Lines of code: 16
