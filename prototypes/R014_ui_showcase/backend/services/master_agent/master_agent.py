# =============================================================================
# AGENTX Master Agent
# =============================================================================
# Master ReAct Agent that orchestrates specialist "junior" agents as tools
# =============================================================================

import asyncio
from typing import TYPE_CHECKING, Callable, Optional, Union

import dspy

from services.master_agent.delivery_planner import DeliveryPlanner, DeliveryPlan
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

        # Initialize pipeline agents (set via set_pipeline_agents or defaults)
        self.analyst: Optional["AnalystAgent"] = None
        self.researcher: Optional["ResearcherAgent"] = None
        self.data_contextualizer: Optional["DataContextualizerAgent"] = None
        self.designer: Optional["DesignerAgent"] = None
        self.widget_selector: Optional["WidgetSelectorAgent"] = None
        self.sequencer: Optional["SequencerAgent"] = None
        self.presenter: Optional["PresenterAgent"] = None
        self.hydrators: list = []

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
        self.hydrators = hydrators

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
        ):
            raise RuntimeError(
                "MasterAgent pipeline agents not initialized. "
                "Call set_pipeline_agents() before forward()."
            )

        # Phase 1: ANALYST - Understand query and context
        analysis_result = self._run_phase(
            "analysis_qa",
            lambda: self.analyst(user_query=user_query, device_context=device_context),  # type: ignore[arg-type]
        )

        # Phase 2: RESEARCHER - Fetch live data
        research_result = self._run_phase(
            "research_qa",
            lambda: self.researcher(analysis=analysis_result),  # type: ignore[arg-type]
        )

        # Phase 3: DATA CONTEXTUALIZER - Rerank, filter, contextualize
        contextualized_result = self._run_phase(
            "contextualization_qa",
            lambda: self.data_contextualizer(research_data=research_result),  # type: ignore[arg-type]
        )

        # Phase 4: ANALYST (Pass 2) - Judge data quality
        judgment_result = self._run_phase(
            "judgment_qa",
            lambda: self.analyst(  # type: ignore[arg-type]
                user_query=user_query,
                device_context=device_context,
                contextualized_data=contextualized_result,
                pass_number=2,
            ),
        )

        # Check if more research is needed
        if judgment_result.get("needs_more_research", False):
            # Loop back to research phase (simplified - would need more sophisticated loop)
            research_result = self._run_phase(
                "research_qa",
                lambda: self.researcher(  # type: ignore[arg-type]
                    analysis=judgment_result,
                    previous_data=research_result,
                ),
            )
            contextualized_result = self._run_phase(
                "contextualization_qa",
                lambda: self.data_contextualizer(research_data=research_result),  # type: ignore[arg-type]
            )

        # Phase 5: DESIGNER - Add POVs, color schemes
        design_result = self._run_phase(
            "design_qa",
            lambda: self.designer(  # type: ignore[arg-type]
                researched_data=contextualized_result,
                analysis=analysis_result,
            ),
        )

        # Phase 6: WIDGET SELECTOR - Choose widgets
        widget_selection = self._run_phase(
            "widget_selection_qa",
            lambda: self.widget_selector(  # type: ignore[arg-type]
                designed_data=design_result,
                device_context=device_context,
            ),
        )

        # Phase 7: SEQUENCER - Plan delivery order
        sequence_plan = self._run_phase(
            "sequence_qa",
            lambda: self.sequencer(  # type: ignore[arg-type]
                widgets=widget_selection.get("widgets", []),
                user_query=user_query,
            ),
        )

        # Phase 8: PRESENTER - Final polish and QA
        presentation_ready = self._run_phase(
            "presentation_qa",
            lambda: self.presenter(  # type: ignore[arg-type]
                widgets=widget_selection.get("widgets", []),
                sequence=sequence_plan.get("sequence", []),
                design=design_result,
            ),
        )

        # Parallel: Hydrate all widgets
        hydrated_widgets = self._run_hydrators(
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

    def _run_phase(self, checkpoint_name: str, phase_func: Callable) -> dict:
        """Run a single pipeline phase with QA checkpoint.

        Args:
            checkpoint_name: Name of the QA checkpoint
            phase_func: Function to execute for this phase

        Returns:
            Phase result data
        """
        try:
            result = phase_func()
            self.qa.validate_checkpoint(checkpoint_name, result)
            self._emit_qa_progress(checkpoint_name, "passed", result)
            return result
        except Exception as e:
            self.qa.mark_failed(checkpoint_name, str(e))
            self._emit_qa_progress(checkpoint_name, "failed", {"error": str(e)})
            raise

    def _run_hydrators(self, presentation_ready: dict) -> list:
        """Run all hydrators in parallel.

        Args:
            presentation_ready: Data from Presenter agent

        Returns:
            List of hydrated widgets
        """
        # Run hydrators synchronously for now (could be async)
        hydrated_widgets = []
        for hydrator in self.hydrators:
            try:
                # Call the hydrator's forward() method with the required arguments
                result = hydrator.forward(
                    presentation_ready=presentation_ready,
                    researched_data=presentation_ready.get("researched_data", {}),
                    design=presentation_ready.get("design_context", {}),
                )
                if result:
                    hydrated_widgets.append(result)
            except Exception:
                # Log but continue with other hydrators
                pass

        return hydrated_widgets

    def _emit_qa_progress(self, checkpoint: str, status: str, data: dict) -> None:
        """Emit QA progress to frontend via callback.

        Args:
            checkpoint: Checkpoint name
            status: Status (passed, failed, running)
            data: Additional data to send
        """
        if self.qa_callback:
            try:
                # Run async callback in sync context
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.create_task(self.qa_callback(checkpoint, status, data))
            except Exception:
                pass  # Silently fail if callback fails

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
