# =============================================================================
# AGENTX Master Agent
# =============================================================================
# Master ReAct Agent that orchestrates specialist "junior" agents as tools
# =============================================================================

from typing import TYPE_CHECKING, Callable, Optional, Union

import dspy

from services.master_agent.delivery_planner import DeliveryPlanner, DeliveryPlan
from services.master_agent.orchestration import (
    HydrationCoordinator,
    PipelineOrchestrator,
)
from services.master_agent.qa_checkpoints import QACheckpointModule

if TYPE_CHECKING:
    from services.hydrators.card_hydrator import CardHydrator
    from services.hydrators.chart_hydrator import ChartHydrator
    from services.hydrators.form_hydrator import FormHydrator
    from services.hydrators.gallery_hydrator import GalleryHydrator
    from services.hydrators.image_hydrator import ImageHydrator
    from services.hydrators.markdown_hydrator import MarkdownHydrator
    from services.pipeline.analyst import AnalystAgent
    from services.pipeline.data_contextualizer import DataContextualizerAgent
    from services.pipeline.designer import DesignerAgent
    from services.pipeline.presenter import PresenterAgent
    from services.pipeline.researcher import ResearcherAgent
    from services.pipeline.sequencer import SequencerAgent
    from services.pipeline.widget_selector import WidgetSelectorAgent


class MasterAgent(dspy.Module):
    """Master ReAct Agent that orchestrates all specialist agents.

    The Master Agent acts as the "Boss" that:
    - Orchestrates all pipeline agents
    - Sets standards based on research
    - Checks format, sequence, quality at each stage
    - Marks TODO checkboxes as items pass QA
    - Final signoff before sending to frontend
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
                "ChartHydrator",
                "MarkdownHydrator",
                "CardHydrator",
                "FormHydrator",
                "ImageHydrator",
                "GalleryHydrator",
            ]
        ],
    ) -> None:
        """Set the pipeline agents and hydrators."""
        self.analyst = analyst
        self.researcher = researcher
        self.data_contextualizer = data_contextualizer
        self.designer = designer
        self.widget_selector = widget_selector
        self.sequencer = sequencer
        self.presenter = presenter
        self.hydration_coordinator = HydrationCoordinator(hydrators)

    def forward(self, user_query: str, device_context: str = "desktop") -> dict:
        """Execute the master agent pipeline.

        Args:
            user_query: The user's query
            device_context: Device context (desktop, mobile, etc.)

        Returns:
            Dict containing delivery plan and QA report
        """
        # Ensure all agents are initialized
        if (
            not self.analyst
            or not self.researcher
            or not self.data_contextualizer
            or not self.designer
            or not self.widget_selector
            or not self.sequencer
            or not self.presenter
            or not self.hydration_coordinator
        ):
            raise RuntimeError(
                "MasterAgent pipeline agents not initialized. "
                "Call set_pipeline_agents() before forward()."
            )

        # Execute pipeline through orchestrator
        pipeline_result = self.pipeline_orchestrator.execute_pipeline(
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

        # Extract results
        sequence_plan = pipeline_result["sequence_plan"]
        presentation_ready = pipeline_result["presentation_ready"]

        # Hydrate widgets
        hydrated_widgets = self.hydration_coordinator.hydrate_widgets(
            presentation_ready=presentation_ready,
        )

        # Final QA checkpoint
        self.qa.validate_checkpoint(
            "hydration_qa",
            {"hydrated_count": len(hydrated_widgets)},
        )

        # Create delivery plan
        delivery_plan = self.delivery_planner.plan_delivery(
            widgets=hydrated_widgets,
            sequence=sequence_plan.get("sequence", []),
        )

        # Finalize QA report
        qa_report = self.qa.finalize_report()

        return {
            "delivery_plan": delivery_plan,
            "qa_report": qa_report,
            "widgets": hydrated_widgets,
        }

    async def execute_with_streaming(
        self,
        user_query: str,
        device_context: str = "desktop",
    ) -> DeliveryPlan:
        """Execute the pipeline with real-time widget streaming.

        Args:
            user_query: The user's query
            device_context: Device context

        Returns:
            DeliveryPlan with staggered widget delivery
        """
        # Run the pipeline
        result = self.forward(user_query, device_context)

        # Stream widgets according to delivery plan
        delivery_plan: DeliveryPlan = result["delivery_plan"]

        if self.widget_callback:
            await self.delivery_planner.deliver_with_delay(
                delivery_plan,
                self.widget_callback,
            )

        return delivery_plan


def create_master_agent(
    widget_callback: Optional[Callable] = None,
    qa_callback: Optional[Callable] = None,
) -> MasterAgent:
    """Factory function to create a MasterAgent instance.

    Args:
        widget_callback: Async callback for widget delivery
        qa_callback: Async callback for QA progress updates

    Returns:
        Configured MasterAgent instance
    """
    return MasterAgent(
        widget_callback=widget_callback,
        qa_callback=qa_callback,
    )
