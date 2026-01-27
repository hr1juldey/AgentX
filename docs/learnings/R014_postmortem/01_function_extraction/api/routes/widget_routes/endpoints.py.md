# Function Extraction: api/routes/widget_routes/endpoints.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/api/routes/widget_routes/endpoints.py`

## File Size
122 lines

## Purpose

    Args:
        widget: Widget DTO from use case

    Returns:
        UIDescriptor for frontend

## Key Classes
None

## Key Functions
- async `generate_widget()`
- async `generate_intelligent()`
- `_convert_dto_to_ui_descriptor()`
- `_create_error_widget()`

## Dependencies
- from datetime import datetime
- from typing import Any
- from fastapi import APIRouter
- from api.models import GenerateRequest, IntelligentGenerateRequest, UIDescriptor
- from application.use_cases.widget_generation import get_widget_generation_use_case
- from application.dtos.requests import GenerateWidgetRequest
- from application.dtos.requests import (

## Data Structures
See key classes above

## Business Logic
This module contains 0 classes and 4 functions.
It focuses on async operations.
Code complexity: 89 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.514195
- Lines of code: 89
