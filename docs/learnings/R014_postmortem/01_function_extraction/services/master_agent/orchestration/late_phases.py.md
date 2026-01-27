# Function Extraction: services/master_agent/orchestration/late_phases.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/master_agent/orchestration/late_phases.py`

## File Size
151 lines

## Purpose

    def __init__(self, executor: PhaseExecutor) -> None:

## Key Classes
- `LatePhases`

## Key Functions
- `__init__()`
- `run_designer_phase()`
- `run_widget_selector_phase()`
- `run_sequencer_phase()`
- `run_presenter_phase()`

## Dependencies
- import logging
- from typing import TYPE_CHECKING, Any
- from services.master_agent.orchestration.data_tracking import (
- from services.master_agent.orchestration.logging import (
- from services.master_agent.orchestration.phase_executor import PhaseExecutor
- from services.pipeline.designer import DesignerAgent
- from services.pipeline.presenter import PresenterAgent
- from services.pipeline.sequencer import SequencerAgent
- from services.pipeline.widget_selector import WidgetSelectorAgent

## Data Structures
See key classes above

## Business Logic
This module contains 1 classes and 5 functions.
It uses synchronous operations.
Code complexity: 125 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.527225
- Lines of code: 125
