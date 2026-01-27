# Function Extraction: services/master_agent/delivery_planner.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/master_agent/delivery_planner.py`

## File Size
86 lines

## Purpose

    widgets: list  # List of UIDescriptor
    delays: list[float]  # Delay in seconds for each widget
    total_duration: float  # Total time for all deliveries

    def get_delivery_schedule(self) -

## Key Classes
- `DeliveryPlan`
- `DeliveryPlanner`

## Key Functions
- async `deliver_with_delay()`
- `get_delivery_schedule()`
- `__init__()`
- `plan_delivery()`

## Dependencies
- from dataclasses import dataclass
- from typing import TYPE_CHECKING
- from services.master_agent.delivery import DeliveryExecution, DeliveryPlanning

## Data Structures
See key classes above

## Business Logic
This module contains 2 classes and 4 functions.
It focuses on async operations.
Code complexity: 62 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.525012
- Lines of code: 62
