# =============================================================================
# AGENTX Presenter - Flow Checker Module
# =============================================================================
# Checks narrative flow and pacing
# =============================================================================

import dspy


class FlowCheckerModule(dspy.Module):
    """Checks narrative flow and pacing.

    Has 2 signatures:
    - CheckNarrativeFlow: Check if widgets tell a coherent story
    - ValidatePacing: Check if pacing is appropriate
    """

    def __init__(self):
        super().__init__()
        self.check_flow = dspy.Predict("sequence, widgets -> flow_analysis, issues")
        self.validate_pacing = dspy.Predict("delays -> pacing_analysis, issues")

    def forward(self, sequence: list, widgets: list) -> dict:
        """Check narrative flow and pacing."""
        sequence_str = str(sequence)
        widgets_str = str(widgets)

        flow_result = self.check_flow(sequence=sequence_str, widgets=widgets_str)

        # Extract delays from sequence for pacing validation
        delays = [s.get("delay_sec", 0) for s in sequence]
        pacing_result = self.validate_pacing(delays=str(delays))

        return {
            "flow_analysis": flow_result.flow_analysis
            if hasattr(flow_result, "flow_analysis")
            else "Coherent flow",
            "flow_issues": flow_result.issues if hasattr(flow_result, "issues") else [],
            "pacing_analysis": pacing_result.pacing_analysis
            if hasattr(pacing_result, "pacing_analysis")
            else "Appropriate pacing",
            "pacing_issues": pacing_result.issues
            if hasattr(pacing_result, "issues")
            else [],
        }
