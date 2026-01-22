# =============================================================================
# AGENTX Delivery Planner - Planning Logic
# =============================================================================
# Widget ordering and delay calculation for staggered delivery
# =============================================================================


class DeliveryPlanning:
    """Handles widget ordering and delay calculation for delivery."""

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
        """Initialize delivery planning.

        Args:
            min_delay: Minimum delay between widgets
            max_delay: Maximum delay between widgets
        """
        self.min_delay = min_delay
        self.max_delay = max_delay

    def order_widgets_by_sequence(
        self,
        widgets: list,
        sequence: list,
    ) -> list:
        """Order widgets according to the planned sequence.

        Args:
            widgets: List of widget descriptors
            sequence: Ordered list from Sequencer agent

        Returns:
            Ordered list of widgets
        """
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

    def calculate_delays(self, widgets: list) -> list[float]:
        """Calculate delivery delays with priority handling.

        Priority widgets (markdown, search-result) get minimal delay.
        Other widgets are spaced 2-5 seconds apart.

        Args:
            widgets: List of widgets to calculate delays for

        Returns:
            List of delay values for each widget
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
