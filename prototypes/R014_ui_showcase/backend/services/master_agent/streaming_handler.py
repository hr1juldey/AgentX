# =============================================================================
# AGENTX Master Agent - Streaming Handler
# =============================================================================
# Handles async streaming execution for MasterAgent
# =============================================================================

from typing import TYPE_CHECKING

from services.master_agent.delivery_planner import DeliveryPlan
from services.master_agent.validation import PipelineValidator

if TYPE_CHECKING:
    from services.master_agent.master_agent import MasterAgent


class StreamingHandler:
    """Handles async streaming execution with real-time widget delivery."""

    def __init__(self, master_agent: "MasterAgent"):
        """Initialize streaming handler.

        Args:
            master_agent: MasterAgent instance
        """
        self.master_agent = master_agent
        self._validator = PipelineValidator(master_agent)

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
        self._validator.validate_streaming_ready()

        # Run the pipeline
        result = self.master_agent.forward(user_query, device_context)

        # Stream widgets according to delivery plan
        return await self.master_agent.streaming_execution.execute_with_streaming(
            result
        )
