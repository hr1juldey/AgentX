# =============================================================================
# AGENTX Hydrators - Chart Hydrator Module
# =============================================================================
# Hydrates chart widgets with proper DSPy signature
# =============================================================================

import dspy
import json
import logging

from services.tools.designer.color_palette import get_chart_colors
from services.tools.hydrators.signatures import ChartData

logger = logging.getLogger(__name__)


class ChartHydratorModule(dspy.Module):
    """Hydrates chart widgets with properly structured data."""

    def __init__(self):
        super().__init__()
        self.generate_chart = dspy.Predict(ChartData)

    def forward(self, presentation_ready: dict) -> dict:
        """Generate chart configuration with structured output."""
        data = presentation_ready.get("researched_data", {})
        design = presentation_ready.get("design", {})
        query = presentation_ready.get("query", "")

        # Extract domain for color selection
        domain = design.get("domain", "general")

        try:
            result = self.generate_chart(
                query=query,
                data=str(data),
                design=str(design),
            )

            # Extract structured output from DSPy result
            chart_title = getattr(result, "chart_title", "Chart")
            chart_type = getattr(result, "chart_type", "bar")
            chart_data_str = getattr(result, "chart_data", "[]")
            x_axis_key = getattr(result, "x_axis_key", "label")
            y_axis_keys_str = getattr(result, "y_axis_keys", "value")

            # Parse chart_data - LLM may return JSON array or Python list string
            try:
                if isinstance(chart_data_str, str):
                    chart_data = json.loads(chart_data_str)
                else:
                    chart_data = (
                        list(chart_data_str)
                        if hasattr(chart_data_str, "__iter__")
                        else []
                    )
            except (json.JSONDecodeError, TypeError):
                logger.warning(f"Failed to parse chart_data: {chart_data_str}")
                chart_data = []

            # Parse y_axis_keys
            if isinstance(y_axis_keys_str, str):
                y_axis_keys = [
                    k.strip() for k in y_axis_keys_str.split(",") if k.strip()
                ]
            else:
                y_axis_keys = [y_axis_keys_str]

            # Get domain-appropriate colors
            colors = get_chart_colors(domain=domain, count=len(y_axis_keys))

            # Build structured content with colors
            content = {
                "title": chart_title,
                "type": chart_type,
                "data": chart_data,
                "x_axis": x_axis_key,
                "y_axis": y_axis_keys,
                "colors": colors,
                "metadata": {
                    "data_points": len(chart_data),
                    "chart_type": chart_type,
                },
            }

            return {
                "descriptor_type": "chart",
                "content": content,
                "metadata": {
                    "chart_type": chart_type,
                    "data_points": len(chart_data),
                    "x_axis": x_axis_key,
                    "y_axis": y_axis_keys,
                    "colors": colors,
                },
            }

        except Exception as e:
            logger.error(f"Chart hydrator error: {e}")
            # Return fallback structure with default colors
            default_colors = get_chart_colors(domain="general", count=1)
            return {
                "descriptor_type": "chart",
                "content": {
                    "title": "Chart",
                    "type": "bar",
                    "data": [],
                    "x_axis": "label",
                    "y_axis": ["value"],
                    "colors": default_colors,
                    "metadata": {"error": str(e)},
                },
                "metadata": {"error": str(e)},
            }
