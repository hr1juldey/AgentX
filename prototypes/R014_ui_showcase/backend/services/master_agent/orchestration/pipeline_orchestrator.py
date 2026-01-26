# =============================================================================
# AGENTX Master Agent - Pipeline Orchestrator
# =============================================================================
# Orchestrates the 10-phase Master Agent pipeline
# =============================================================================

import logging
from typing import TYPE_CHECKING, Any, Callable

from services.master_agent.orchestration.early_phases import EarlyPhases
from services.master_agent.orchestration.late_phases import LatePhases
from services.master_agent.orchestration.pipeline_execution import execute_pipeline
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
        return execute_pipeline(
            early=self.early,
            late=self.late,
            analyst=analyst,
            researcher=researcher,
            data_contextualizer=data_contextualizer,
            designer=designer,
            widget_selector=widget_selector,
            sequencer=sequencer,
            presenter=presenter,
            user_query=user_query,
            device_context=device_context,
        )
