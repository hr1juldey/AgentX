# =============================================================================
# AGENTX Card Hydrator
# =============================================================================
# Fills card widgets with stat data + color scheme
# =============================================================================

import logging
import uuid
from datetime import datetime

from typing import Any

import dspy
from services.tools.hydrators import CardHydratorModule

logger = logging.getLogger(__name__)


class CardHydrator(dspy.Module):
    """Card Hydrator: Fills card widgets with statistical data.

    Creates stat cards with key metrics, using color scheme
    from designer for visual consistency.
    """

    def __init__(self):
        super().__init__()
        self.hydrator = CardHydratorModule()

    def forward(
        self,
        presentation_ready: dict,
        researched_data: dict,
        design: dict,
    ) -> dict[str, Any]:
        """Hydrate card widget with stats.

        Args:
            presentation_ready: Output from PRESENTER agent
            researched_data: Research output from RESEARCHER/CONTEXTUALIZER
            design: Design output from DESIGNER agent

        Returns:
            Card widget descriptor with hydrated stat cards
        """
        beautiful_data = researched_data.get("beautiful_data", {})
        color_scheme = design.get("color_scheme", {})
        insights = design.get("insights", [])

        # Log what we received for debugging
        logger.info("  📊 [CARD HYDRATOR] Received data:")
        logger.info(f"      - beautiful_data keys: {list(beautiful_data.keys())}")
        logger.info(f"      - insights: {len(insights)} items")
        logger.info(
            f"      - color_scheme: {list(color_scheme.keys()) if color_scheme else 'none'}"
        )

        # Prepare data for hydration
        hydration_input = {
            "researched_data": {
                "key_facts": beautiful_data.get("key_facts", []),
                "trends": beautiful_data.get("trends", {}),
            },
            "design": {
                "color_scheme": color_scheme,
                "insights": insights,
            },
            "insights": insights,
        }

        # Generate stat cards
        stat_cards = self.hydrator(presentation_ready=hydration_input)

        # Extract content from result (DSPy Predict returns special object)
        content = stat_cards.get("content", []) if hasattr(stat_cards, "get") else []

        return {
            "id": str(uuid.uuid4())[:8],
            "type": "card",
            "timestamp": datetime.utcnow().isoformat(),
            "content": content,
            "metadata": {
                "color_scheme": color_scheme,
                "card_count": len(content),
            },
        }


def create_card_hydrator() -> CardHydrator:
    """Factory function for CardHydrator."""
    return CardHydrator()
