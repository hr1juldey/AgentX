# Function Extraction: services/master_agent/agent_setup.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/master_agent/agent_setup.py`

## File Size
83 lines

## Purpose

    def __init__(self, master_agent):

## Key Classes
- `AgentSetup`

## Key Functions
- `__init__()`
- `set_pipeline_agents()`

## Dependencies
- from typing import TYPE_CHECKING, Union
- from services.master_agent.execution import PipelineExecution
- from services.master_agent.factory import StreamingExecution
- from services.master_agent.orchestration import HydrationCoordinator
- from services.tools.hydrators import (
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
This module contains 1 classes and 2 functions.
It uses synchronous operations.
Code complexity: 67 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.524091
- Lines of code: 67
