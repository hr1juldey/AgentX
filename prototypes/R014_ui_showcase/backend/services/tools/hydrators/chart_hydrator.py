# =============================================================================
# AGENTX Hydrators - Chart Hydrator Module
# =============================================================================
# Hydrates chart widgets with data
# =============================================================================

import dspy


class ChartHydratorModule(dspy.Module):
    """Hydrates chart widgets with data."""

    def __init__(self):
        super().__init__()
        self.generate_chart_config = dspy.Predict("data, design -> chart_config")

    def forward(self, presentation_ready: dict) -> dict:
        """Generate chart configuration."""
        data = presentation_ready.get("researched_data", {})
        design = presentation_ready.get("design", {})

        config_result = self.generate_chart_config(data=str(data), design=str(design))

        return {
            "descriptor_type": "chart",
            "content": config_result.chart_config
            if hasattr(config_result, "chart_config")
            else {},
        }
