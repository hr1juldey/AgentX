"""UI widget operations for UIDSPyAgent.

Handles widget selection, card display, confirmation dialogs, and progress updates.
"""

import dspy
from typing import Any, Dict

from agentx.agent.dspy_signatures.ui_signatures import (
    RequestConfirmationSignature,
    ShowCardSignature,
    UpdateProgressSignature,
)
from agentx.agent.dspy_signatures.widgets.selection import SelectWidgetSignature
from agentx.agent.tools.common.dspy_helpers import safe_extract


class UIWidgetOperations:
    """Widget operation handlers for UI agent."""

    def __init__(self) -> None:
        """Initialize widget operation signatures."""
        self.widget_selector = dspy.Predict(SelectWidgetSignature)
        self.card_generator = dspy.Predict(ShowCardSignature)
        self.confirmation_requester = dspy.Predict(RequestConfirmationSignature)
        self.progress_updater = dspy.Predict(UpdateProgressSignature)

    def select_widget(
        self,
        query: str,
        content_type: str,
        content_summary: str,
        existing_widgets: str,
    ) -> Dict[str, Any]:
        """Select appropriate UI widget for content presentation.

        Args:
            query: User's original question
            content_type: Type of content (text, data, image, form, etc.)
            content_summary: Brief summary of the content
            existing_widgets: Already shown widget types (avoid duplicates)

        Returns:
            dict with selected_widget, confidence, reasoning
        """
        result = self.widget_selector(
            query=query,
            content_type=content_type,
            content_summary=content_summary,
            existing_widgets=existing_widgets,
        )

        return {
            "selected_widget": safe_extract(result, "selected_widget", "card"),
            "confidence": safe_extract(result, "confidence", 0.5),
            "reasoning": safe_extract(result, "reasoning", ""),
        }

    def show_card(
        self,
        title: str,
        content: str,
        context: str,
    ) -> Dict[str, Any]:
        """Generate card widget with title and content.

        Args:
            title: Card title
            content: Card content (markdown supported)
            context: Additional context

        Returns:
            dict with show_actions and card_descriptor
        """
        result = self.card_generator(
            title=title,
            content=content,
            context=context,
        )

        show_actions = safe_extract(result, "show_actions", False)
        card_descriptor = safe_extract(result, "card_descriptor", {})

        return {
            "show_actions": show_actions,
            "card_descriptor": card_descriptor,
        }

    def request_confirmation(
        self,
        action_description: str,
        risk_level: str,
    ) -> Dict[str, Any]:
        """Request user confirmation for an action.

        Args:
            action_description: Description of action to confirm
            risk_level: Risk level (low, medium, high)

        Returns:
            dict with confirmation_dialog
        """
        result = self.confirmation_requester(
            action_description=action_description,
            risk_level=risk_level,
        )

        confirmation_dialog = safe_extract(result, "confirmation_dialog", {})
        return {"confirmation_dialog": confirmation_dialog}

    def update_progress(
        self,
        task_name: str,
        current_step: int,
        total_steps: int,
    ) -> Dict[str, Any]:
        """Update progress indicator for a long-running task.

        Args:
            task_name: Name of the task
            current_step: Current step number (1-indexed)
            total_steps: Total number of steps

        Returns:
            dict with progress_descriptor
        """
        result = self.progress_updater(
            task_name=task_name,
            current_step=current_step,
            total_steps=total_steps,
        )

        progress_descriptor = safe_extract(result, "progress_descriptor", {})
        return {"progress_descriptor": progress_descriptor}
