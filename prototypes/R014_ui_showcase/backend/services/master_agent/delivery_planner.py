# =============================================================================
# AGENTX Delivery Planner Module
# =============================================================================
# Staggered delivery logic for consultant-style widget presentation
# =============================================================================

import asyncio
from dataclasses import dataclass
from typing import TYPE_CHECKING

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

    # Default timing between widgets (consultant-style: 2-5 seconds)
    DEFAULT_MIN_DELAY = 2.0
    DEFAULT_MAX_DELAY = 5.0

    # Priority widgets that get delivered first
    PRIORITY_WIDGETS = ["markdown", "search-result"]

    def __init__(
        self,
        min_delay: float = DEFAULT_MIN_DELAY,
        max_delay: float = DEFAULT_MAX_DELAY,
    ):
        self.min_delay = min_delay
        self.max_delay = max_delay

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
        ordered_widgets = self._order_widgets_by_sequence(widgets, sequence)
        delays = self._calculate_delays(ordered_widgets)

        total_duration = sum(delays) if delays else 0

        return DeliveryPlan(
            widgets=ordered_widgets,
            delays=delays,
            total_duration=total_duration,
        )

    def _order_widgets_by_sequence(
        self,
        widgets: list,
        sequence: list,
    ) -> list:
        """Order widgets according to the planned sequence."""
        ordered = []
        for seq_item in sequence:
            widget_type = seq_item.get("widget", "")
            for w in widgets:
                if hasattr(w, "descriptor_type") and w.descriptor_type == widget_type:
                    if w not in ordered:
                        ordered.append(w)
                        break

        # Add any remaining widgets not in sequence
        for w in widgets:
            if w not in ordered:
                ordered.append(w)

        return ordered

    def _calculate_delays(self, widgets: list) -> list[float]:
        """Calculate delivery delays with priority handling.

        Priority widgets (markdown, search-result) get minimal delay.
        Other widgets are spaced 2-5 seconds apart.
        """
        delays = []
        accumulated_delay = 0.0

        for i, widget in enumerate(widgets):
            widget_type = getattr(widget, "descriptor_type", "")

            # First widget or priority widgets: immediate or quick
            if i == 0:
                # First widget gets minimal delay (or 0 for immediate)
                delay = 0.0
            elif widget_type in self.PRIORITY_WIDGETS:
                delay = self.min_delay / 2  # Priority widgets get faster delivery
            else:
                # Standard spacing between widgets
                delay = self.min_delay + (
                    (self.max_delay - self.min_delay) * (i / max(len(widgets) - 1, 1))
                )

            delays.append(accumulated_delay + delay)
            accumulated_delay += delay

        return delays

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
        tasks = []
        for delay, widget in delivery_plan.get_delivery_schedule():
            # Schedule each widget delivery with its delay
            task = asyncio.create_task(
                self._deliver_after_delay(delay, widget, delivery_callback)
            )
            tasks.append(task)

        # Wait for all deliveries to complete
        await asyncio.gather(*tasks)

    async def _deliver_after_delay(
        self,
        delay: float,
        widget: dict,
        callback,
    ) -> None:
        """Deliver a single widget after its delay."""
        await asyncio.sleep(delay)
        await callback(widget)
