# =============================================================================
# AGENTX R014 - Text Widget Generators
# =============================================================================
# Generate content for markdown, card, and form widgets
# =============================================================================

from datetime import datetime

import dspy

from api.dspy_signatures import (
    CardContentSignature,
    FormContentSignature,
    MarkdownContentSignature,
)
from api.models import UIDescriptor


class TextWidgetGenerator:
    """Generate content for text-based widgets."""

    @staticmethod
    async def generate_markdown(prompt: str) -> UIDescriptor:
        """Generate markdown content."""
        generator = dspy.Predict(MarkdownContentSignature)
        result = generator(topic=prompt)
        return UIDescriptor(
            id=f"markdown-{datetime.now().timestamp()}",
            type="markdown",
            timestamp=datetime.now().isoformat(),
            content=result.content,
            metadata={"format": "markdown"},
        )

    @staticmethod
    async def generate_card(prompt: str) -> UIDescriptor:
        """Generate card content."""
        generator = dspy.Predict(CardContentSignature)
        result = generator(topic=prompt)
        return UIDescriptor(
            id=f"card-{datetime.now().timestamp()}",
            type="card",
            timestamp=datetime.now().isoformat(),
            title=result.title,
            content=result.content,
            metadata={
                "icon": "sparkles",
                "actions": [
                    {"label": "Learn More", "action": "more", "variant": "outline"}
                ],
            },
        )

    @staticmethod
    async def generate_form(prompt: str) -> UIDescriptor:
        """Generate form content."""
        generator = dspy.Predict(FormContentSignature)
        result = generator(form_type=prompt)
        return UIDescriptor(
            id=f"form-{datetime.now().timestamp()}",
            type="form",
            timestamp=datetime.now().isoformat(),
            title=result.title,
            content=result.description,
            metadata={
                "form_id": "dynamic-form",
                "submit_label": "Submit",
                "fields": [
                    {
                        "name": "response",
                        "type": "textarea",
                        "label": "Your Response",
                        "required": True,
                        "placeholder": "Type here...",
                    }
                ],
            },
        )
