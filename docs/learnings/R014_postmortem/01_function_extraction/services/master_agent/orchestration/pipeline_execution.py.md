# Function Extraction: services/master_agent/orchestration/pipeline_execution.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/master_agent/orchestration/pipeline_execution.py`

## File Size
138 lines

## Purpose

Handles the main execution flow including early phases, late phases.

## Key Classes
None

## Key Functions
- `execute_pipeline()`

## Dependencies
- import logging
- from typing import TYPE_CHECKING, Any
- from services.master_agent.orchestration.early_phases import EarlyPhases
- from services.master_agent.orchestration.late_phases import LatePhases
- from services.master_agent.orchestration.pipeline_additional_research import (
- from services.pipeline.analyst import AnalystAgent
- from services.pipeline.data_contextualizer import DataContextualizerAgent
- from services.pipeline.designer import DesignerAgent
- from services.pipeline.presenter import PresenterAgent
- from services.pipeline.researcher import ResearcherAgent
- from services.pipeline.sequencer import SequencerAgent
- from services.pipeline.widget_selector import WidgetSelectorAgent

## Data Structures
See key classes above

## Business Logic
This module contains 0 classes and 1 functions.
It uses synchronous operations.
Code complexity: 104 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.528185
- Lines of code: 104
