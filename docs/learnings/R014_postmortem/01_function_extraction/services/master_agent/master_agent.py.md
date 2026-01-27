# Function Extraction: services/master_agent/master_agent.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/master_agent/master_agent.py`

## File Size
148 lines

## Purpose

    Orchestrates pipeline agents, sets standards based on research,
    checks format/sequence/quality at each stage, and provides
    final signoff before sending to frontend.

## Key Classes
- `MasterAgent`

## Key Functions
- async `execute_with_streaming()`
- `__init__()`
- `set_pipeline_agents()`
- `forward()`

## Dependencies
- from typing import TYPE_CHECKING, Callable, Optional, Union
- import dspy
- from services.master_agent.agent_setup import AgentSetup
- from services.master_agent.delivery_planner import DeliveryPlanner, DeliveryPlan
- from services.master_agent.execution import PipelineExecution
- from services.master_agent.factory import StreamingExecution
- from services.master_agent.orchestration import (
- from services.master_agent.qa_checkpoints import QACheckpointModule
- from services.master_agent.streaming_handler import StreamingHandler
- from services.master_agent.validation import PipelineValidator
- from services.tools.hydrators import (
- from services.pipeline.analyst import AnalystAgent
- from services.pipeline.data_contextualizer import DataContextualizerAgent
- from services.pipeline.designer import DesignerAgent
- from services.pipeline.presenter import PresenterAgent
- ... and 3 more

## Data Structures
See key classes above

## Business Logic
This module contains 1 classes and 4 functions.
It focuses on async operations.
Code complexity: 120 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.525964
- Lines of code: 120
