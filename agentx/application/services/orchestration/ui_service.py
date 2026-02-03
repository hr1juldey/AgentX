"""UI service for server-driven UI management.

Handles form interrupt/resume logic and UI state management.
Following LangGraph server-driven UI pattern (C007).
"""

from uuid import UUID
from typing import Any

from agentx.application.dtos.ui_dtos import (
    FormComponentDTO,
)


class UIService:
    """Service for UI state management.

    Handles:
    - Form interrupt/resume logic
    - UI component state tracking
    - LangGraph server-driven UI integration
    """

    def __init__(self) -> None:
        """Initialize the UI service."""
        # Track active forms by session
        self._active_forms: dict[UUID, dict[str, Any]] = {}

    async def trigger_form_interrupt(
        self,
        session_id: UUID,
        form_descriptor: FormComponentDTO,
    ) -> None:
        """Trigger a form interrupt for user input.

        Pauses agent execution and requests user input via form.

        Args:
            session_id: Session identifier.
            form_descriptor: Form component to display.
        """
        self._active_forms[session_id] = {
            "form": form_descriptor.model_dump(),
            "status": "awaiting_input",
        }

    async def on_form_submit(
        self,
        session_id: UUID,
        form_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Handle form submission and resume agent execution.

        Args:
            session_id: Session identifier.
            form_data: Submitted form data.

        Returns:
            dict: Result to inject back into agent execution.

        Raises:
            ValueError: If no active form for session.
        """
        if session_id not in self._active_forms:
            msg = f"No active form for session {session_id}"
            raise ValueError(msg)

        # Validate form data against schema (if present)
        # active_form = self._active_forms[session_id]
        # validation_result = self._validate_form_data(form_data, active_form["form"])

        # Clear active form
        del self._active_forms[session_id]

        # Return data for agent to continue
        return {
            "form_data": form_data,
            "status": "submitted",
        }

    def has_active_form(self, session_id: UUID) -> bool:
        """Check if session has an active form interrupt.

        Args:
            session_id: Session identifier.

        Returns:
            bool: True if active form exists.
        """
        return session_id in self._active_forms

    def get_active_form(self, session_id: UUID) -> dict[str, Any] | None:
        """Get active form for session.

        Args:
            session_id: Session identifier.

        Returns:
            dict | None: Active form data or None.
        """
        return self._active_forms.get(session_id)
