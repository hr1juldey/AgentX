# =============================================================================
# AGENTX Master Agent - Pipeline Agent Setup
# =============================================================================
# Agent configuration and initialization logic
# =============================================================================

from typing import TYPE_CHECKING, Union

from services.master_agent.execution import PipelineExecution
from services.master_agent.factory import StreamingExecution
from services.master_agent.orchestration import HydrationCoordinator

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


class AgentSetup:
    """Handles pipeline agent configuration and initialization."""

    def __init__(self, master_agent):
        """Initialize agent setup.

        Args:
            master_agent: MasterAgent instance to configure
        """
        self.master_agent = master_agent

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
        self.master_agent.analyst = analyst
        self.master_agent.researcher = researcher
        self.master_agent.data_contextualizer = data_contextualizer
        self.master_agent.designer = designer
        self.master_agent.widget_selector = widget_selector
        self.master_agent.sequencer = sequencer
        self.master_agent.presenter = presenter
        self.master_agent.hydration_coordinator = HydrationCoordinator(hydrators)

        # Initialize execution modules
        self.master_agent.pipeline_execution = PipelineExecution(
            self.master_agent.pipeline_orchestrator,
            self.master_agent.hydration_coordinator,
            self.master_agent.delivery_planner,
            self.master_agent.qa,
        )
        self.master_agent.streaming_execution = StreamingExecution(
            self.master_agent.delivery_planner,
            self.master_agent.widget_callback,
        )
