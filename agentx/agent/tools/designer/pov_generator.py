"""POV Generator Module for Designer agent.

Ported from R014: services/tools/designer/pov_generator.py

Generates point of view for UI widget design.
Selects appropriate widget types based on content and state.

Fraud #16 fix: Returns dspy.Prediction instead of dict.
"""

import dspy

from agentx.agent.dspy_signatures.designer.pov import DesignPOV
from agentx.agent.tools.common.dspy_helpers import safe_extract


class POVGeneratorModule(dspy.Module):
    """Generates point of view for widget design.

    Determines:
    - Best widget type for content
    - Widget properties
    - Rationale for selection

    STATE AWARE: Checks existing widgets to avoid duplicates.

    Fraud #16 fix: Returns dspy.Prediction instead of dict.
    """

    def __init__(self) -> None:
        """Initialize the POV generator."""
        super().__init__()
        self.designer = dspy.ChainOfThought(DesignPOV)

    def forward(
        self,
        query: str,
        content: str,
        existing_widgets: list[str],
    ) -> dspy.Prediction:
        """Generate point of view for widget design.

        Args:
            query: User's original question
            content: Content to present
            existing_widgets: List of already shown widget types

        Returns:
            dspy.Prediction with widget recommendation and properties
        """
        # Build existing widgets string
        existing_str = ", ".join(existing_widgets) if existing_widgets else "none"

        # Run designer
        result = self.designer(
            query=query,
            content=content,
            existing_widgets=existing_str,
        )

        # Extract recommendations
        recommended_widget = safe_extract(result, "recommended_widget", "card")
        widget_props = safe_extract(result, "widget_props", "{}")
        rationale = safe_extract(result, "rationale", "")

        # Parse widget props as JSON - handle None value
        import json

        if widget_props is None:
            widget_props = "{}"
        if not isinstance(widget_props, str):
            widget_props = str(widget_props)

        try:
            props_dict = json.loads(widget_props)
        except (json.JSONDecodeError, TypeError, ValueError):
            props_dict = {}

        return dspy.Prediction(
            recommended_widget=recommended_widget,
            widget_props=props_dict,
            rationale=rationale,
        )
