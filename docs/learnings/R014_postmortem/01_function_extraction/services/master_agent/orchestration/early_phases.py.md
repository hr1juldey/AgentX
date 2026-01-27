# Function Extraction: services/master_agent/orchestration/early_phases.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/master_agent/orchestration/early_phases.py`

## File Size
148 lines

## Purpose

    def __init__(self, executor: PhaseExecutor) -> None:

## Key Classes
- `EarlyPhases`

## Key Functions
- `__init__()`
- `run_analyst_phase()`
- `run_researcher_phase()`
- `run_contextualizer_phase()`
- `run_analyst_judgment_phase()`

## Dependencies
- import logging
- from typing import TYPE_CHECKING, Any
- from services.master_agent.orchestration.data_tracking import (
- from services.master_agent.orchestration.logging import (
- from services.master_agent.orchestration.phase_executor import PhaseExecutor
- from services.pipeline.analyst import AnalystAgent
- from services.pipeline.data_contextualizer import DataContextualizerAgent
- from services.pipeline.researcher import ResearcherAgent

## Data Structures
See key classes above

## Business Logic
This module contains 1 classes and 5 functions.
It uses synchronous operations.
Code complexity: 121 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.526719
- Lines of code: 121
