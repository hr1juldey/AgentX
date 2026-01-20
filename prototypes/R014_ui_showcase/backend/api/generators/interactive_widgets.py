# =============================================================================
# AGENTX R014 - Interactive Widget Generators
# =============================================================================
# Generate content for progress, action, and confirmation widgets
# =============================================================================

from datetime import datetime

import dspy

from api.dspy_signatures import (
    ActionContentSignature,
    ConfirmationContentSignature,
    ProgressContentSignature,
)
from api.models import UIDescriptor


class InteractiveWidgetGenerator:
    """Generate content for interactive widgets."""

    @staticmethod
    async def generate_progress(prompt: str) -> UIDescriptor:
        """Generate progress content."""
        generator = dspy.Predict(ProgressContentSignature)
        result = generator(task=prompt)
        return UIDescriptor(
            id=f"progress-{datetime.now().timestamp()}",
            type="progress",
            timestamp=datetime.now().isoformat(),
            title="Processing",
            content=result.status_text,
            metadata={
                "value": 0.6,
                "indeterminate": False,
                "status_text": result.status_text,
            },
        )

    @staticmethod
    async def generate_action(prompt: str) -> UIDescriptor:
        """Generate action button content."""
        generator = dspy.Predict(ActionContentSignature)
        result = generator(action_type=prompt)
        return UIDescriptor(
            id=f"action-{datetime.now().timestamp()}",
            type="action",
            timestamp=datetime.now().isoformat(),
            title=result.description,
            content="Click the button below",
            metadata={
                "button_text": result.button_text,
                "action_id": "action_click",
                "variant": "default",
            },
        )

    @staticmethod
    async def generate_confirmation(prompt: str) -> UIDescriptor:
        """Generate confirmation dialog content."""
        generator = dspy.Predict(ConfirmationContentSignature)
        result = generator(action=prompt)
        return UIDescriptor(
            id=f"confirmation-{datetime.now().timestamp()}",
            type="confirmation",
            timestamp=datetime.now().isoformat(),
            title=result.title,
            content=result.message,
            metadata={
                "confirm_label": "Confirm",
                "cancel_label": "Cancel",
                "confirm_action": "confirm_yes",
                "cancel_action": "confirm_no",
                "variant": "default",
            },
        )
