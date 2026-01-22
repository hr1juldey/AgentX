# =============================================================================
# AGENTX Master Agent - Pipeline Execution
# =============================================================================
# Core pipeline execution logic for MasterAgent
# =============================================================================

from services.master_agent.delivery_planner import DeliveryPlanner


class PipelineExecution:
    """Handles core pipeline execution logic."""

    def __init__(
        self,
        pipeline_orchestrator,
        hydration_coordinator,
        delivery_planner: DeliveryPlanner,
        qa,
    ):
        """Initialize pipeline execution.

        Args:
            pipeline_orchestrator: Pipeline orchestrator instance
            hydration_coordinator: Hydration coordinator instance
            delivery_planner: Delivery planner instance
            qa: QA checkpoint module
        """
        self.pipeline_orchestrator = pipeline_orchestrator
        self.hydration_coordinator = hydration_coordinator
        self.delivery_planner = delivery_planner
        self.qa = qa

    def execute(
        self,
        analyst,
        researcher,
        data_contextualizer,
        designer,
        widget_selector,
        sequencer,
        presenter,
        user_query: str,
        device_context: str,
    ) -> dict:
        """Execute the master agent pipeline.

        Args:
            analyst: Analyst agent
            researcher: Researcher agent
            data_contextualizer: Data contextualizer agent
            designer: Designer agent
            widget_selector: Widget selector agent
            sequencer: Sequencer agent
            presenter: Presenter agent
            user_query: User's query
            device_context: Device context

        Returns:
            Dict containing delivery plan, QA report, and widgets
        """
        # Execute pipeline through orchestrator
        pipeline_result = self.pipeline_orchestrator.execute_pipeline(
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
