# =============================================================================
# AGENTX Chart Hydrator
# =============================================================================
# Fills chart widgets with data + POV overlay
# =============================================================================

import uuid
from datetime import datetime

from typing import Any

import dspy

from services.tools.hydrators import ChartHydratorModule


class ChartHydrator(dspy.Module):
    """Chart Hydrator: Fills chart widgets with researched data.

    Creates chart configurations with real data, POV overlays,
    and appropriate color schemes from the designer.
    """

    def __init__(self):
        super().__init__()
        self.hydrator = ChartHydratorModule()

    def forward(
        self,
        presentation_ready: dict,
        researched_data: dict,
        design: dict,
    ) -> dict[str, Any]:
        """Hydrate chart widget with data.

        Args:
            presentation_ready: Output from PRESENTER agent
            researched_data: Research output from RESEARCHER/CONTEXTUALIZER
            design: Design output from DESIGNER agent

        Returns:
            Chart widget descriptor with hydrated content
        """
        beautiful_data = researched_data.get("beautiful_data", {})
        color_scheme = design.get("color_scheme", {})
        points_of_view = design.get("points_of_view", [])

        # Prepare data for hydration
        hydration_input = {
            "researched_data": {
                "key_facts": beautiful_data.get("key_facts", []),
                "trends": beautiful_data.get("trends", {}),
                "comparisons": beautiful_data.get("comparisons", []),
                "structured_data": researched_data.get("structured_data", {}),
            },
            "design": {
                "color_scheme": color_scheme,
                "points_of_view": points_of_view,
                "visual_hierarchy": design.get("visual_hierarchy", []),
            },
        }

        # Generate chart configuration
        chart_config = self.hydrator(presentation_ready=hydration_input)

        # Extract content from result (DSPy Predict returns special object)
        content = (
            chart_config.get("content", {}) if hasattr(chart_config, "get") else {}
        )

        return {
            "id": str(uuid.uuid4())[:8],
            "type": "chart",
            "timestamp": datetime.utcnow().isoformat(),
            "content": content,
            "metadata": {
                "color_scheme": color_scheme,
                "pov_count": len(points_of_view),
                "data_source": "researched",
            },
        }


def create_chart_hydrator() -> ChartHydrator:
    """Factory function for ChartHydrator."""
    return ChartHydrator()
