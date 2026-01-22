# =============================================================================
# AGENTX Hydrators - Form Hydrator Module
# =============================================================================
# Hydrates form widgets with action items
# =============================================================================

import dspy


class FormHydratorModule(dspy.Module):
    """Hydrates form widgets with action items."""

    def __init__(self):
        super().__init__()
        self.generate_form = dspy.Predict("insights, data -> form_fields")

    def forward(self, presentation_ready: dict) -> dict:
        """Generate form fields."""
        insights = presentation_ready.get("insights", [])
        data = presentation_ready.get("researched_data", {})

        form_result = self.generate_form(insights=str(insights), data=str(data))

        return {
            "descriptor_type": "form",
            "content": form_result.form_fields
            if hasattr(form_result, "form_fields")
            else [],
        }
