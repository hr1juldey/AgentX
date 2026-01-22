# =============================================================================
# AGENTX Master Agent
# =============================================================================
# Master ReAct Agent that orchestrates specialist "junior" agents as tools
# =============================================================================

from typing import TYPE_CHECKING, Callable, Optional, Union

import dspy

from services.master_agent.agent_setup import AgentSetup
from services.master_agent.delivery_planner import DeliveryPlanner, DeliveryPlan
from services.master_agent.execution import PipelineExecution
from services.master_agent.factory import StreamingExecution
from services.master_agent.orchestration import (
    HydrationCoordinator,
    PipelineOrchestrator,
)
from services.master_agent.qa_checkpoints import QACheckpointModule
from services.master_agent.streaming_handler import StreamingHandler
from services.master_agent.validation import PipelineValidator

if TYPE_CHECKING:
    from services.tools.hydrators import (
        CardHydratorModule,
        ChartHydratorModule,
        FormHydratorModule,
        GalleryHydratorModule,
        ImageHydratorModule,
        MarkdownHydratorModule,
    )
    from services.pipeline.analyst import AnalystAgent
    from services.pipeline.data_contextualizer import DataContextualizerAgent
    from services.pipeline.designer import DesignerAgent
    from services.pipeline.presenter import PresenterAgent
    from services.pipeline.researcher import ResearcherAgent
    from services.pipeline.sequencer import SequencerAgent
    from services.pipeline.widget_selector import WidgetSelectorAgent


class MasterAgent(dspy.Module):
    """Master ReAct Agent that orchestrates all specialist agents.

    Orchestrates pipeline agents, sets standards based on research,
    checks format/sequence/quality at each stage, and provides
    final signoff before sending to frontend.
    """

    def __init__(
        self,
        widget_callback: Optional[Callable] = None,
        qa_callback: Optional[Callable] = None,
    ):
        super().__init__()
        self.qa = QACheckpointModule()
        self.delivery_planner = DeliveryPlanner()
        self.widget_callback = widget_callback
        self.qa_callback = qa_callback

        # Orchestration modules
        self.pipeline_orchestrator = PipelineOrchestrator(self.qa, qa_callback)
        self.hydration_coordinator: Optional[HydrationCoordinator] = None

        # Execution modules
        self.pipeline_execution: Optional[PipelineExecution] = None
        self.streaming_execution: Optional[StreamingExecution] = None

        # Helpers
        self._agent_setup = AgentSetup(self)
        self._validator = PipelineValidator(self)
        self._streaming_handler = StreamingHandler(self)

        # Initialize pipeline agents (set via set_pipeline_agents or defaults)
        self.analyst: Optional["AnalystAgent"] = None
        self.researcher: Optional["ResearcherAgent"] = None
        self.data_contextualizer: Optional["DataContextualizerAgent"] = None
        self.designer: Optional["DesignerAgent"] = None
        self.widget_selector: Optional["WidgetSelectorAgent"] = None
        self.sequencer: Optional["SequencerAgent"] = None
        self.presenter: Optional["PresenterAgent"] = None

    def set_pipeline_agents(
        self,
        analyst: "AnalystAgent",
        researcher: "ResearcherAgent",
        data_contextualizer: "DataContextualizerAgent",
        designer: "DesignerAgent",
        widget_selector: "WidgetSelectorAgent",
        sequencer: "SequencerAgent",
        presenter: "PresenterAgent",
        hydrators: list[
            Union[
                "ChartHydratorModule",
                "MarkdownHydratorModule",
                "CardHydratorModule",
                "FormHydratorModule",
                "ImageHydratorModule",
                "GalleryHydratorModule",
            ]
        ],
    ) -> None:
        """Set the pipeline agents and hydrators."""
        self._agent_setup.set_pipeline_agents(
            analyst,
            researcher,
            data_contextualizer,
            designer,
            widget_selector,
            sequencer,
            presenter,
            hydrators,
        )

    def forward(self, user_query: str, device_context: str = "desktop") -> dict:
        """Execute the master agent pipeline.

        Args:
            user_query: The user's query
            device_context: Device context (desktop, mobile, etc.)

        Returns:
            Dict containing delivery plan and QA report
        """
        self._validator.validate_agents_initialized()

        return self.pipeline_execution.execute(
            analyst=self.analyst,
            researcher=self.researcher,
            data_contextualizer=self.data_contextualizer,
            designer=self.designer,
            widget_selector=self.widget_selector,
            sequencer=self.sequencer,
            presenter=self.presenter,
            user_query=user_query,
            device_context=device_context,
        )

    async def execute_with_streaming(
        self,
        user_query: str,
        device_context: str = "desktop",
    ) -> DeliveryPlan:
        """Execute pipeline with real-time widget streaming."""
        return await self._streaming_handler.execute_with_streaming(
            user_query,
            device_context,
        )
