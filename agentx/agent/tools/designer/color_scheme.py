"""Color Scheme Module for Designer agent.

Ported from R014: services/tools/designer/color_scheme.py

Designs color schemes for UI widgets based on content purpose.
"""

import dspy

from agentx.agent.dspy_signatures.designer.pov import DesignColors
from agentx.agent.tools.common.dspy_helpers import safe_extract


class ColorSchemeModule(dspy.Module):
    """Designs color schemes for widgets.

    Selects appropriate colors based on:
    - Content type (data, text, media)
    - User intent (inform, alert, guide)
    - Purpose (info, warning, success, error)
    """

    def __init__(self) -> None:
        """Initialize the color scheme module."""
        super().__init__()
        self.designer = dspy.Predict(DesignColors)

    def forward(
        self,
        widget_type: str,
        content_purpose: str = "info",
    ) -> dict:
        """Design color scheme for widget.

        Args:
            widget_type: Type of widget being colored
            content_purpose: Purpose of the content (default: "info")

        Returns:
            dict with color scheme (primary, secondary, background, text, border)
        """
        # Run color designer
        result = self.designer(
            widget_type=widget_type,
            content_purpose=content_purpose,
        )

        # Extract color scheme
        color_scheme_str = safe_extract(result, "color_scheme", "{}")

        # Parse as JSON
        import json

        try:
            color_scheme = json.loads(color_scheme_str)
        except json.JSONDecodeError:
            # Fallback to default colors
            color_scheme = {
                "primary": "#00D9FF",
                "secondary": "#1E1E1E",
                "background": "#0A0A0A",
                "text": "#FFFFFF",
                "border": "#333333",
            }

        return color_scheme
