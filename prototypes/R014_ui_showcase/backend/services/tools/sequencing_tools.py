# =============================================================================
# AGENTX Sequencer Tools
# =============================================================================
# DSPy modules for the SEQUENCER agent (What Order?)
# =============================================================================

import dspy


class FlowPlannerModule(dspy.Module):
    """Plans narrative flow for widget delivery.

    Has 3 signatures:
    - PlanNarrativeArc: Plan story flow (hook → context → insight → action)
    - OptimizeFlow: Optimize flow for engagement
    - ValidateSequence: Validate sequence makes sense
    """

    def __init__(self):
        super().__init__()
        self.plan_arc = dspy.Predict("widgets, query -> narrative_arc, sequence")
        self.optimize_flow = dspy.Predict("sequence -> optimized_sequence")
        self.validate_sequence = dspy.Predict("sequence -> is_valid, feedback")

    def forward(self, widgets: list, user_query: str = "") -> dict:
        """Plan narrative flow for widgets."""
        widgets_str = str(widgets)

        arc_result = self.plan_arc(widgets=widgets_str, query=user_query)

        if hasattr(arc_result, "sequence"):
            sequence = [
                seq.strip()
                for seq in str(arc_result.sequence).split(",")
                if seq.strip()
            ]

            # Optimize the flow
            optimize_result = self.optimize_flow(sequence=sequence)

            # Validate the sequence
            validate_result = self.validate_sequence(
                sequence=str(
                    optimize_result.optimized_sequence
                    if hasattr(optimize_result, "optimized_sequence")
                    else sequence
                )
            )

            return {
                "sequence": sequence,
                "narrative_arc": arc_result.narrative_arc
                if hasattr(arc_result, "narrative_arc")
                else "hook → context → insight → action",
                "optimized_sequence": optimize_result.optimized_sequence
                if hasattr(optimize_result, "optimized_sequence")
                else sequence,
                "is_valid": validate_result.is_valid == "true"
                if hasattr(validate_result, "is_valid")
                else True,
            }

        return {
            "sequence": widgets,
            "narrative_arc": "hook → context → insight → action",
            "is_valid": True,
        }


class PacingCalculatorModule(dspy.Module):
    """Calculates timing delays for staggered delivery.

    Has 2 signatures:
    - CalculateDelays: Calculate delays between widgets
    - AdjustPacing: Adjust pacing based on widget complexity
    """

    def __init__(self):
        super().__init__()
        self.calculate_delays = dspy.Predict("sequence, widgets -> delays")
        self.adjust_pacing = dspy.Predict("sequence, complexity -> adjusted_delays")

    def forward(self, widgets: list, sequence: list) -> dict:
        """Calculate pacing for widget delivery."""
        # Default delays: 2-5 seconds apart
        num_widgets = len(sequence)
        min_delay = 2.0
        max_delay = 5.0

        delays = []
        accumulated_delay = 0.0

        for i, seq_item in enumerate(sequence):
            if i == 0:
                delay = 0.0  # First widget is immediate
            else:
                # Calculate delay between widgets
                delay = min_delay + (
                    (max_delay - min_delay) * (i / max(num_widgets - 1, 1))
                )

            delays.append(
                {
                    "widget": seq_item.get("widget", ""),
                    "order": seq_item.get("order", i + 1),
                    "delay_sec": accumulated_delay + delay,
                }
            )
            accumulated_delay += delay

        return {
            "sequence": delays,
            "total_duration": accumulated_delay,
        }
