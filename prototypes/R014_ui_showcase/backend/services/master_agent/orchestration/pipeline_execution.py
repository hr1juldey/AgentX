# =============================================================================
# AGENTX Master Agent - Pipeline Execution Logic
# =============================================================================
# Core pipeline execution flow
# =============================================================================

"""Core pipeline execution logic.

Handles the main execution flow including early phases, late phases.
"""

import logging
from typing import TYPE_CHECKING, Any

from services.master_agent.orchestration.early_phases import EarlyPhases
from services.master_agent.orchestration.late_phases import LatePhases
from services.master_agent.orchestration.pipeline_additional_research import (
    execute_additional_research,
)

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from services.pipeline.analyst import AnalystAgent
    from services.pipeline.data_contextualizer import DataContextualizerAgent
    from services.pipeline.designer import DesignerAgent
    from services.pipeline.presenter import PresenterAgent
    from services.pipeline.researcher import ResearcherAgent
    from services.pipeline.sequencer import SequencerAgent
    from services.pipeline.widget_selector import WidgetSelectorAgent


def execute_pipeline(
    early: EarlyPhases,
    late: LatePhases,
    analyst: "AnalystAgent",
    researcher: "ResearcherAgent",
    data_contextualizer: "DataContextualizerAgent",
    designer: "DesignerAgent",
    widget_selector: "WidgetSelectorAgent",
    sequencer: "SequencerAgent",
    presenter: "PresenterAgent",
    user_query: str,
    device_context: str,
) -> dict[str, Any]:
    """Execute the full 8-phase pipeline.

    Args:
        early: Early phases executor
        late: Late phases executor
        analyst: Analyst agent instance
        researcher: Research agent instance
        data_contextualizer: Data contextualizer instance
        designer: Designer agent instance
        widget_selector: Widget selector instance
        sequencer: Sequencer instance
        presenter: Presenter instance
        user_query: User's query
        device_context: Device context

    Returns:
        Dict with sequence plan, design result, widget selection, etc.
    """
    # Phase 1: ANALYST - Understand query and context
    analysis_result = early.run_analyst_phase(
        analyst,
        user_query,
        device_context,
    )

    # Phase 2: RESEARCHER - Fetch live data
    research_result = early.run_researcher_phase(
        researcher,
        analysis_result,
    )

    # Phase 3: DATA CONTEXTUALIZER - Rerank, filter, contextualize
    contextualized_result = early.run_contextualizer_phase(
        data_contextualizer,
        research_result,
    )

    # Phase 4: ANALYST (Pass 2) - Judge data quality
    judgment_result = early.run_analyst_judgment_phase(
        analyst,
        user_query,
        device_context,
        contextualized_result,
    )

    # Check if more research is needed
    if judgment_result.get("needs_more_research", False):
        contextualized_result = execute_additional_research(
            early,
            researcher,
            data_contextualizer,
            judgment_result,
            contextualized_result,
        )

    # Phase 5: DESIGNER - Add POVs, color schemes
    design_result = late.run_designer_phase(
        designer,
        contextualized_result,
        analysis_result,
    )

    # Phase 6: WIDGET SELECTOR - Choose widgets
    widget_selection = late.run_widget_selector_phase(
        widget_selector,
        design_result,
        device_context,
    )

    # Phase 7: SEQUENCER - Plan delivery order
    sequence_plan = late.run_sequencer_phase(
        sequencer,
        widget_selection,
        user_query,
    )

    # Phase 8: PRESENTER - Final polish and QA
    presentation_ready = late.run_presenter_phase(
        presenter,
        widget_selection,
        sequence_plan,
        design_result,
        contextualized_result,  # Pass research data for hydrators
    )

    return {
        "sequence_plan": sequence_plan,
        "design_result": design_result,
        "widget_selection": widget_selection,
        "presentation_ready": presentation_ready,
        "researched_data": contextualized_result,  # Include for hydrators
    }
