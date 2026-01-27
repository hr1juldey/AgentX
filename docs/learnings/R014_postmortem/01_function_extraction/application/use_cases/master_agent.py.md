# Function Extraction: application/use_cases/master_agent.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/application/use_cases/master_agent.py`

## File Size
113 lines

## Purpose

    This is a facade that wraps the existing Master Agent
    to provide a clean architectural boundary.

    Phase 1: Returns the factory function (no behavior changes).
    Phase 3: Will implement 

## Key Classes
- `MasterAgentUseCase`

## Key Functions
- `create_master_agent()`
- `setup_master_agent_with_pipeline()`
- `get_master_agent_use_case()`

## Dependencies
- from services.master_agent import create_master_agent
- from config.settings import settings
- from services.hydrators.card_hydrator import CardHydrator
- from services.hydrators.chart_hydrator import ChartHydrator
- from services.hydrators.form_hydrator import FormHydrator
- from services.hydrators.gallery_hydrator import GalleryHydrator
- from services.hydrators.image_hydrator import ImageHydrator
- from services.hydrators.markdown_hydrator import MarkdownHydrator
- from services.master_agent import DeliveryPlan, create_master_agent
- from services.pipeline.analyst import AnalystAgent
- from services.pipeline.data_contextualizer import DataContextualizerAgent
- from services.pipeline.designer import DesignerAgent
- from services.pipeline.presenter import PresenterAgent
- from services.pipeline.researcher import ResearcherAgent
- from services.pipeline.sequencer import SequencerAgent
- ... and 1 more

## Data Structures
See key classes above

## Business Logic
This module contains 1 classes and 3 functions.
It uses synchronous operations.
Code complexity: 82 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.516316
- Lines of code: 82
