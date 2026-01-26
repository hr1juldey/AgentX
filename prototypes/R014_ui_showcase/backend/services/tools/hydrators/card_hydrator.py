# =============================================================================
# AGENTX Hydrators - Card Hydrator Module
# =============================================================================
# Hydrates card widgets with proper DSPy signature
# =============================================================================

import dspy
import json
import logging

from services.tools.hydrators.widget_signatures import CardData
from services.tools.researcher.number_extractor_utils import strip_markdown_wrapper

logger = logging.getLogger(__name__)


class CardHydratorModule(dspy.Module):
    """Hydrates card widgets with properly structured card data."""

    def __init__(self):
        super().__init__()
        self.generate_cards = dspy.Predict(CardData)

    def forward(self, presentation_ready: dict) -> dict:
        """Generate card configuration with structured output."""
        data = presentation_ready.get("researched_data", {})
        design = presentation_ready.get("design", {})
        query = presentation_ready.get("query", "")

        try:
            result = self.generate_cards(
                query=query,
                data=str(data),
                design=str(design),
            )

            # Extract structured output
            cards_str = getattr(result, "cards", "[]")

            # Parse cards - LLM may return JSON array
            try:
                if isinstance(cards_str, str):
                    # Strip markdown code block wrapper (14B coder models)
                    cards_str = strip_markdown_wrapper(cards_str)
                    cards = json.loads(cards_str)
                elif isinstance(cards_str, list):
                    cards = cards_str
                else:
                    cards = []
            except (json.JSONDecodeError, TypeError):
                logger.warning(f"Failed to parse cards: {cards_str}")
                cards = []

            # Validate card structure
            validated_cards = []
            for card in cards if isinstance(cards, list) else []:
                if isinstance(card, dict):
                    validated_cards.append(
                        {
                            "title": card.get("title", "Metric"),
                            "value": card.get("value", "N/A"),
                            "description": card.get("description", ""),
                            "icon": card.get("icon", "📊"),
                            "color": card.get("color", "blue_500"),
                        }
                    )

            return {
                "descriptor_type": "card",
                "content": {"cards": validated_cards},
                "metadata": {"card_count": len(validated_cards)},
            }

        except Exception as e:
            logger.error(f"Card hydrator error: {e}")
            return {
                "descriptor_type": "card",
                "content": {"cards": []},
                "metadata": {"card_count": 0, "error": str(e)},
            }
