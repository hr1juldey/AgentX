# =============================================================================
# AGENTX Master Agent - Pipeline Orchestrator
# =============================================================================
# Orchestrates the 10-phase Master Agent pipeline
# =============================================================================

import logging
from typing import TYPE_CHECKING, Any, Callable

from services.master_agent.orchestration.early_phases import EarlyPhases
from services.master_agent.orchestration.late_phases import LatePhases
from services.master_agent.orchestration.phase_executor import PhaseExecutor
from services.master_agent.qa_checkpoints import QACheckpointModule

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from services.pipeline.analyst import AnalystAgent
    from services.pipeline.data_contextualizer import DataContextualizerAgent
    from services.pipeline.designer import DesignerAgent
    from services.pipeline.presenter import PresenterAgent
    from services.pipeline.researcher import ResearcherAgent
    from services.pipeline.sequencer import SequencerAgent
    from services.pipeline.widget_selector import WidgetSelectorAgent


class PipelineOrchestrator:
    """Orchestrates the 10-phase Master Agent pipeline.

    Manages sequential execution with QA checkpoints.
    """

    def __init__(
        self,
        qa: QACheckpointModule,
        qa_callback: Callable | None = None,
    ) -> None:
        """Initialize pipeline orchestrator.

        Args:
            qa: QA checkpoint module
            qa_callback: Optional callback for QA progress
        """
        executor = PhaseExecutor(qa, qa_callback)
        self.early = EarlyPhases(executor)
        self.late = LatePhases(executor)

    def execute_pipeline(
        self,
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
        """Execute the full pipeline.

        Args:
            analyst: Analyst agent instance
            researcher: Researcher agent instance
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
        analysis_result = self.early.run_analyst_phase(
            analyst,
            user_query,
            device_context,
        )

        # Phase 2: RESEARCHER - Fetch live data
        research_result = self.early.run_researcher_phase(
            researcher,
            analysis_result,
        )

        # Phase 3: DATA CONTEXTUALIZER - Rerank, filter, contextualize
        contextualized_result = self.early.run_contextualizer_phase(
            data_contextualizer,
            research_result,
        )

        # Phase 4: ANALYST (Pass 2) - Judge data quality
        judgment_result = self.early.run_analyst_judgment_phase(
            analyst,
            user_query,
            device_context,
            contextualized_result,
        )

        # Check if more research is needed
        if judgment_result.get("needs_more_research", False):
            logger.info("  [RESEARCHER] Additional research needed...")
            research_result = self.early.run_researcher_phase(
                researcher,
                judgment_result,
            )
            contextualized_result = self.early.run_contextualizer_phase(
                data_contextualizer,
                research_result,
            )

        # Phase 5: DESIGNER - Add POVs, color schemes
        design_result = self.late.run_designer_phase(
            designer,
            contextualized_result,
            analysis_result,
        )

        # Phase 6: WIDGET SELECTOR - Choose widgets
        widget_selection = self.late.run_widget_selector_phase(
            widget_selector,
            design_result,
            device_context,
        )

        # Phase 7: SEQUENCER - Plan delivery order
        sequence_plan = self.late.run_sequencer_phase(
            sequencer,
            widget_selection,
            user_query,
        )

        # Phase 8: PRESENTER - Final polish and QA
        presentation_ready = self.late.run_presenter_phase(
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
