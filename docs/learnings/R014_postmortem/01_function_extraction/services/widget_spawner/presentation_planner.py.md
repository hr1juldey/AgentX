# Function Extraction: services/widget_spawner/presentation_planner.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/widget_spawner/presentation_planner.py`

## File Size
104 lines

## Purpose

    content_analysis: str = dspy.InputField(desc="Content type, complexity")
    user_intent: str = dspy.InputField(desc="Goal: explore/compare/decide")
    device_context: str = dspy.InputField(desc

## Key Classes
- `PlanPresentationSignature`
- `PresentationPlannerAgent`

## Key Functions
- `__init__()`
- `forward()`

## Dependencies
- import json
- import logging
- from typing import Dict, Any
- import dspy
- from services.widget_spawner.layout_utils import generate_positions
- from services.widget_spawner.rewards import presentation_quality_score

## Data Structures
See key classes above

## Business Logic
This module contains 2 classes and 2 functions.
It uses synchronous operations.
Code complexity: 73 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.566523
- Lines of code: 73
