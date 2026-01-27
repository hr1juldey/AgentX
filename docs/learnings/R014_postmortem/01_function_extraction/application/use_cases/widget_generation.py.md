# Function Extraction: application/use_cases/widget_generation.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/application/use_cases/widget_generation.py`

## File Size
76 lines

## Purpose

    This is a facade that wraps the existing WidgetSpawnerService
    to provide a clean architectural boundary.

    Returns domain entities, not DTOs.

## Key Classes
- `WidgetGenerationUseCase`

## Key Functions
- async `generate_widget()`
- async `generate_intelligent()`
- `get_widget_generation_use_case()`

## Dependencies
- from application.dtos.requests import GenerateWidgetRequest, IntelligentGenerateRequest
- from domain.entities.ui_descriptor import UIDescriptor
- from services.widget_spawner import get_widget_spawner_service
- from services.widget_spawner.intelligent_agent import IntelligentUIGenerator

## Data Structures
See key classes above

## Business Logic
This module contains 1 classes and 3 functions.
It focuses on async operations.
Code complexity: 50 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.516905
- Lines of code: 50
