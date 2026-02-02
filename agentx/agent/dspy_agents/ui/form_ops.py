"""Form operations for UIDSPyAgent.

Handles form configuration and schema generation.
"""

import dspy
from typing import Any, Dict, List

from agentx.agent.dspy_signatures.ui_signatures import ConfigureFormSignature
from agentx.agent.tools.common.dspy_helpers import safe_extract


class UIFormOperations:
    """Form operation handlers for UI agent."""

    def __init__(self) -> None:
        """Initialize form operation signatures."""
        self.form_configurer = dspy.Predict(ConfigureFormSignature)

    def configure_form(
        self,
        required_fields: List[str],
        context: str,
    ) -> Dict[str, Any]:
        """Configure form schema for user input.

        Args:
            required_fields: Fields required from user
            context: Context for form configuration

        Returns:
            dict with form_schema
        """
        result = self.form_configurer(
            required_fields=required_fields,
            context=context,
        )

        form_schema = safe_extract(result, "form_schema", {})
        return {"form_schema": form_schema}
