# =============================================================================
# AGENTX Hydrators - Form Hydrator Module
# =============================================================================
# Hydrates form widgets with proper DSPy signature
# =============================================================================

import dspy
import json
import logging

from services.tools.hydrators.signatures import FormData

logger = logging.getLogger(__name__)


class FormHydratorModule(dspy.Module):
    """Hydrates form widgets with properly structured field data."""

    def __init__(self):
        super().__init__()
        self.generate_form = dspy.Predict(FormData)

    def forward(self, presentation_ready: dict) -> dict:
        """Generate form configuration with structured output."""
        data = presentation_ready.get("researched_data", {})
        insights = presentation_ready.get("insights", [])
        query = presentation_ready.get("query", "")

        try:
            result = self.generate_form(
                query=query,
                data=str(data),
                insights=str(insights),
            )

            # Extract structured output
            fields_str = getattr(result, "form_fields", "[]")

            # Parse fields
            try:
                if isinstance(fields_str, str):
                    fields = json.loads(fields_str)
                elif isinstance(fields_str, list):
                    fields = fields_str
                else:
                    fields = []
            except (json.JSONDecodeError, TypeError):
                logger.warning(f"Failed to parse form_fields: {fields_str}")
                fields = []

            # Validate field structure (match frontend FormWidget interface)
            validated_fields = []
            for field in fields if isinstance(fields, list) else []:
                if isinstance(field, dict):
                    label = field.get("label", "Field")
                    # Generate name from label (snake_case for form submission)
                    name = label.lower().replace(" ", "_").replace("-", "_")
                    validated_fields.append(
                        {
                            "name": name,
                            "type": field.get("type", "text"),
                            "label": label,
                            "placeholder": field.get(
                                "description", ""
                            ),  # Map description→placeholder
                            "options": field.get("options", []),
                        }
                    )

            return {
                "descriptor_type": "form",
                "content": {"form_fields": validated_fields},
                "metadata": {"field_count": len(validated_fields)},
            }

        except Exception as e:
            logger.error(f"Form hydrator error: {e}")
            return {
                "descriptor_type": "form",
                "content": {"form_fields": []},
                "metadata": {"field_count": 0, "error": str(e)},
            }
