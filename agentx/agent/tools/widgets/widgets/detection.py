"""Pattern detection for widget selection.

Detects content patterns in research findings to map to widget types.
"""

import dspy

from agentx.agent.tools.widgets.widgets.signatures import (
    DetectContentPatternSignature,
)


class DetectContentPatternModule(dspy.Module):
    """DSPy module for detecting content patterns.

    Analyzes research findings and identifies patterns
    that map to specific widget types.
    """

    def __init__(self):
        """Initialize pattern detection module."""
        super().__init__()
        self.detect_patterns = dspy.Predict(DetectContentPatternSignature)

    def forward(self, query: str, research_findings: list[str]) -> dspy.Prediction:
        """Detect content patterns in findings.

        Args:
            query: User's query
            research_findings: Accumulated research findings

        Returns:
            dspy.Prediction: Pattern detection results
        """
        findings_text = "\n".join(f"- {f}" for f in research_findings)

        return self.detect_patterns(  # type: ignore[return-value]
            query=query,
            research_findings=findings_text,
        )


def infer_widgets_from_patterns(result: dspy.Prediction) -> list[str]:
    """Infer widget types from detected patterns.

    Args:
        result: Pattern detection result

    Returns:
        list[str]: Suggested widget types
    """
    widget_types = []

    # Map patterns to widgets
    if result.has_comparison.lower() == "true":  # type: ignore[attr-defined]
        widget_types.append("data_table")

    if result.has_temporal_data.lower() == "true":  # type: ignore[attr-defined]
        widget_types.append("timeline")
        widget_types.append("chart")

    if result.has_geographic_data.lower() == "true":  # type: ignore[attr-defined]
        widget_types.append("map")

    if result.has_ranking.lower() == "true":  # type: ignore[attr-defined]
        widget_types.append("data_table")

    # Default: text card
    if not widget_types:
        widget_types.append("text_card")

    return widget_types
