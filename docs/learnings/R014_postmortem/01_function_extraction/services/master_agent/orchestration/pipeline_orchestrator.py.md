# Function Extraction: services/master_agent/orchestration/pipeline_orchestrator.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/master_agent/orchestration/pipeline_orchestrator.py`

## File Size
90 lines

## Purpose

    Manages sequential execution with QA checkpoints.

## Key Classes
- `PipelineOrchestrator`

## Key Functions
- `__init__()`
- `execute_pipeline()`

## Dependencies
- import logging
- from typing import TYPE_CHECKING, Any, Callable
- from services.master_agent.orchestration.early_phases import EarlyPhases
- from services.master_agent.orchestration.late_phases import LatePhases
- from services.master_agent.orchestration.pipeline_execution import execute_pipeline
- from services.master_agent.orchestration.phase_executor import PhaseExecutor
- from services.master_agent.qa_checkpoints import QACheckpointModule
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
Code complexity: 72 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.528426
- Lines of code: 72
