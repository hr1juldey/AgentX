# =============================================================================
# AGENTX Form Hydrator
# =============================================================================
# Fills form widgets with action items based on insights
# =============================================================================

import logging
import uuid
from datetime import datetime

from typing import Any

import dspy
from services.tools.hydrators import FormHydratorModule

logger = logging.getLogger(__name__)


class FormHydrator(dspy.Module):
    """Form Hydrator: Fills form widgets with action items.

    Creates interactive forms based on insights and analysis,
    enabling users to take action on the information presented.
    """

    def __init__(self):
        super().__init__()
        self.hydrator = FormHydratorModule()

    def forward(
        self,
        presentation_ready: dict,
        researched_data: dict,
        design: dict,
    ) -> dict[str, Any]:
        """Hydrate form widget with action items.

        Args:
            presentation_ready: Output from PRESENTER agent
            researched_data: Research output from RESEARCHER/CONTEXTUALIZER
            design: Design output from DESIGNER agent

        Returns:
            Form widget descriptor with hydrated form fields
        """
        insights = design.get("insights", [])
        beautiful_data = researched_data.get("beautiful_data", {})

        # Log what we received for debugging
        logger.info("  📊 [FORM HYDRATOR] Received data:")
        logger.info(f"      - beautiful_data keys: {list(beautiful_data.keys())}")
        logger.info(f"      - insights: {len(insights)} items")

        # Prepare data for hydration
        hydration_input = {
            "insights": insights,
            "researched_data": {
                "key_facts": beautiful_data.get("key_facts", []),
                "trends": beautiful_data.get("trends", {}),
            },
        }

        # Generate form fields
        form_fields = self.hydrator(presentation_ready=hydration_input)

        # Extract content from result (DSPy Predict returns special object)
        content = form_fields.get("content", []) if hasattr(form_fields, "get") else []

        return {
            "id": str(uuid.uuid4())[:8],
            "type": "form",
            "timestamp": datetime.utcnow().isoformat(),
            "content": content,
            "metadata": {
                "field_count": len(content),
                "insight_count": len(insights),
            },
        }


def create_form_hydrator() -> FormHydrator:
    """Factory function for FormHydrator."""
    return FormHydrator()
