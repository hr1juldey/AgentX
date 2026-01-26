# =============================================================================
# AGENTX Hydrators - Form Hydrator Module
# =============================================================================
# Hydrates form widgets with proper DSPy signature
# =============================================================================

import dspy
import json
import logging

from services.tools.hydrators.widget_signatures import (
    FormFieldDetails,
    FormFieldNames,
)
from services.tools.researcher.number_extractor_utils import strip_markdown_wrapper

logger = logging.getLogger(__name__)


class FormHydratorModule(dspy.Module):
    """Hydrates form widgets with properly structured field data."""

    def __init__(self):
        super().__init__()
        self.get_field_names = dspy.Predict(FormFieldNames)
        self.get_field_details = dspy.Predict(FormFieldDetails)

    def forward(self, presentation_ready: dict) -> dict:
        """Generate form configuration using split signatures."""
        data = presentation_ready.get("researched_data", {})
        insights = presentation_ready.get("insights", [])
        query = presentation_ready.get("query", "")

        validated_fields = []

        try:
            # Step 1: Get field names (simple task)
            names_result = self.get_field_names(
                query=query, data=str(data), insights=str(insights)
            )
            field_names_str = getattr(names_result, "field_names", "[]")

            # Parse field names (JSON array of strings)
            try:
                if isinstance(field_names_str, str):
                    # Strip markdown code block wrapper (14B coder models)
                    field_names_str = strip_markdown_wrapper(field_names_str)
                    field_names = json.loads(field_names_str)
                elif isinstance(field_names_str, list):
                    field_names = field_names_str
                else:
                    field_names = []
            except (json.JSONDecodeError, TypeError):
                logger.warning(f"Failed to parse field_names: {field_names_str}")
                field_names = []

            logger.info(f"[FORM HYDRATOR] Got {len(field_names)} field names")

            # Step 2: Get details for each field (focused task)
            for field_name in field_names:
                if not isinstance(field_name, str):
                    continue

                try:
                    details_result = self.get_field_details(
                        field_name=field_name, query=query, data=str(data)
                    )

                    field_type = getattr(details_result, "field_type", "text")
                    description = getattr(details_result, "description", "")
                    options_str = getattr(details_result, "options", "[]")

                    # Parse options (JSON array of strings)
                    try:
                        if isinstance(options_str, str):
                            # Strip markdown code block wrapper (14B coder models)
                            options_str = strip_markdown_wrapper(options_str)
                            options = json.loads(options_str)
                        elif isinstance(options_str, list):
                            options = options_str
                        else:
                            options = []
                    except (json.JSONDecodeError, TypeError):
                        logger.warning(
                            f"Failed to parse options for '{field_name}': {options_str}"
                        )
                        options = []

                    # Generate name from label (snake_case for form submission)
                    name = field_name.lower().replace(" ", "_").replace("-", "_")

                    validated_fields.append(
                        {
                            "name": name,
                            "type": field_type
                            if field_type
                            in ["text", "textarea", "number", "select", "checkbox"]
                            else "text",
                            "label": field_name,
                            "placeholder": description,
                            "options": options if isinstance(options, list) else [],
                        }
                    )

                except Exception as e:
                    logger.warning(
                        f"Failed to get details for field '{field_name}': {e}"
                    )
                    continue

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
