# =============================================================================
# AGENTX Hydrators - Card Hydrator Module
# =============================================================================
# Hydrates card widgets with stat data
# =============================================================================

import dspy


class CardHydratorModule(dspy.Module):
    """Hydrates card widgets with stat data."""

    def __init__(self):
        super().__init__()
        self.extract_stats = dspy.Predict("data, design -> stat_cards")

    def forward(self, presentation_ready: dict) -> dict:
        """Extract stat cards from data."""
        data = presentation_ready.get("researched_data", {})
        design = presentation_ready.get("design", {})

        stats_result = self.extract_stats(data=str(data), design=str(design))

        return {
            "descriptor_type": "card",
            "content": stats_result.stat_cards
            if hasattr(stats_result, "stat_cards")
            else [],
        }
