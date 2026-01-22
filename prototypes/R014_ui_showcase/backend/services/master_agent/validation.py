# =============================================================================
# AGENTX Master Agent - Validation
# =============================================================================
# Pipeline agent validation logic
# =============================================================================


class PipelineValidator:
    """Validates pipeline agent initialization."""

    def __init__(self, master_agent):
        """Initialize validator.

        Args:
            master_agent: MasterAgent instance to validate
        """
        self.master_agent = master_agent

    def validate_agents_initialized(self) -> None:
        """Ensure all pipeline agents are initialized.

        Raises:
            RuntimeError: If any agent is not initialized
        """
        if (
            not self.master_agent.analyst
            or not self.master_agent.researcher
            or not self.master_agent.data_contextualizer
            or not self.master_agent.designer
            or not self.master_agent.widget_selector
            or not self.master_agent.sequencer
            or not self.master_agent.presenter
            or not self.master_agent.hydration_coordinator
            or not self.master_agent.pipeline_execution
        ):
            raise RuntimeError(
                "MasterAgent pipeline agents not initialized. "
                "Call set_pipeline_agents() before forward()."
            )

    def validate_streaming_ready(self) -> None:
        """Ensure streaming execution is ready.

        Raises:
            RuntimeError: If streaming execution is not initialized
        """
        if not self.master_agent.streaming_execution:
            raise RuntimeError(
                "MasterAgent not initialized. Call set_pipeline_agents() first."
            )
