# =============================================================================
# AGENTX Delivery Planner Module
# =============================================================================
# Staggered delivery logic for consultant-style widget presentation
# =============================================================================

from dataclasses import dataclass
from typing import TYPE_CHECKING

from services.master_agent.delivery import DeliveryExecution, DeliveryPlanning

if TYPE_CHECKING:
    pass


@dataclass
class DeliveryPlan:
    """Plan for delivering widgets with staggered timing."""

    widgets: list  # List of UIDescriptor
    delays: list[float]  # Delay in seconds for each widget
    total_duration: float  # Total time for all deliveries

    def get_delivery_schedule(self) -> list[tuple[float, dict]]:
        """Get the delivery schedule as list of (delay, widget) tuples."""
        return [
            (delay, widget.model_dump() if hasattr(widget, "model_dump") else widget)
            for delay, widget in zip(self.delays, self.widgets)
        ]


class DeliveryPlanner:
    """Plans staggered widget delivery with consultant-style pacing."""

    def __init__(
        self,
        min_delay: float = 2.0,
        max_delay: float = 5.0,
    ):
        """Initialize delivery planner.

        Args:
            min_delay: Minimum delay between widgets
            max_delay: Maximum delay between widgets
        """
        self._planning = DeliveryPlanning(min_delay, max_delay)
        self._execution = DeliveryExecution()

    def plan_delivery(
        self,
        widgets: list,
        sequence: list,
    ) -> DeliveryPlan:
        """Create a delivery plan with staggered timing.

        Args:
            widgets: List of hydrated widget descriptors
            sequence: Ordered list from Sequencer agent

        Returns:
            DeliveryPlan with calculated delays
        """
        ordered_widgets = self._planning.order_widgets_by_sequence(widgets, sequence)
        delays = self._planning.calculate_delays(ordered_widgets)

        total_duration = sum(delays) if delays else 0

        return DeliveryPlan(
            widgets=ordered_widgets,
            delays=delays,
            total_duration=total_duration,
        )

    async def deliver_with_delay(
        self,
        delivery_plan: DeliveryPlan,
        delivery_callback,
    ) -> None:
        """Execute staggered delivery with async delays.

        Args:
            delivery_plan: The planned delivery schedule
            delivery_callback: Async function to call for each widget delivery
        """
        await self._execution.deliver_with_delay(delivery_plan, delivery_callback)
