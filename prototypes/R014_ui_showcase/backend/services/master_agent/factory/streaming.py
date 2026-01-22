# =============================================================================
# AGENTX Master Agent - Streaming Execution
# =============================================================================
# Async streaming execution logic for real-time widget delivery
# =============================================================================

from services.master_agent.delivery_planner import DeliveryPlan


class StreamingExecution:
    """Handles async streaming execution with real-time widget delivery."""

    def __init__(self, delivery_planner, widget_callback=None):
        """Initialize streaming execution.

        Args:
            delivery_planner: Delivery planner instance
            widget_callback: Optional callback for widget delivery
        """
        self.delivery_planner = delivery_planner
        self.widget_callback = widget_callback

    async def execute_with_streaming(
        self,
        execution_result: dict,
    ) -> DeliveryPlan:
        """Execute the pipeline with real-time widget streaming.

        Args:
            execution_result: Result from pipeline execution

        Returns:
            DeliveryPlan with staggered widget delivery
        """
        # Stream widgets according to delivery plan
        delivery_plan: DeliveryPlan = execution_result["delivery_plan"]

        if self.widget_callback:
            await self.delivery_planner.deliver_with_delay(
                delivery_plan,
                self.widget_callback,
            )

        return delivery_plan
