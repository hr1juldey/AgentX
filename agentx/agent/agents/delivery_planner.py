"""Delivery Planner for Sequencer agent.

Ported from R014: services/pipeline/sequencer.py

Implements staggered delivery pattern for presenting multiple widgets.
Pacing: 0s, 2s, 3.5s, then converging to 5s between widgets.
"""

from typing import Any


class DeliveryPlanner:
    """Plans staggered delivery of multiple widgets.

    Implements the R014 staggered delivery pattern:
    - Widget 1: 0s (immediate)
    - Widget 2: 2s delay
    - Widget 3: 3.5s delay
    - Widget 4+: 5s delay (converged)

    This prevents overwhelming the user with too many widgets at once.
    """

    def __init__(self) -> None:
        """Initialize the delivery planner."""
        # Staggered delivery timings (in seconds)
        self.initial_delays = [0, 2, 3.5]
        self.converged_delay = 5.0

    def plan_delivery(
        self,
        widgets: list[dict[str, Any]],
        urgency: str = "routine",
    ) -> list[dict[str, Any]]:
        """Plan delivery schedule for multiple widgets.

        Args:
            widgets: List of widget dicts with type and props
            urgency: Urgency level (immediate, routine, background)

        Returns:
            list of widget dicts with added timing information
        """
        planned_widgets = []

        for i, widget in enumerate(widgets):
            # Calculate delay based on position
            if i < len(self.initial_delays):
                delay = self.initial_delays[i]
            else:
                delay = self.converged_delay

            # Adjust for urgency
            if urgency == "immediate":
                delay = delay * 0.5  # Faster for urgent
            elif urgency == "background":
                delay = delay * 1.5  # Slower for background

            # Add timing to widget
            planned_widget = {
                **widget,
                "timing": {
                    "delay": delay,
                    "position": i,
                    "total": len(widgets),
                },
            }

            planned_widgets.append(planned_widget)

        return planned_widgets

    def calculate_pacing(
        self,
        num_widgets: int,
        urgency: str = "routine",
    ) -> dict[str, Any]:
        """Calculate pacing information for widget delivery.

        Args:
            num_widgets: Number of widgets to deliver
            urgency: Urgency level

        Returns:
            dict with pacing information (total_time, delays, etc.)
        """
        delays: list[float] = []
        for i in range(num_widgets):
            if i < len(self.initial_delays):
                delay = self.initial_delays[i]
            else:
                delay = self.converged_delay

            # Adjust for urgency
            if urgency == "immediate":
                delay = delay * 0.5
            elif urgency == "background":
                delay = delay * 1.5

            delays.append(delay)

        total_time = sum(delays)

        return {
            "num_widgets": num_widgets,
            "delays": delays,
            "total_time": total_time,
            "urgency": urgency,
        }
