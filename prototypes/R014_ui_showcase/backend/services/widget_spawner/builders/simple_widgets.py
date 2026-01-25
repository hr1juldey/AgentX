# =============================================================================
# AGENTX Widget Spawner - Simple Widget Builders
# =============================================================================
# Helper functions for building simple widget data (no DSPy results)
# =============================================================================

from datetime import datetime
from typing import Any

from services.widget_spawner.config import (
    DEFAULT_ACTION_BUTTON_TEXT,
    DEFAULT_ACTION_ID,
    DEFAULT_CANCEL_LABEL,
    DEFAULT_CONFIRM_LABEL,
)


def build_action_widget(user_query: str, widget_id: str) -> dict[str, Any]:
    """Build action widget data."""
    return {
        "id": widget_id,
        "type": "action",
        "title": "Quick Action",
        "content": f"Action requested: {user_query}",
        "metadata": {
            "button_text": DEFAULT_ACTION_BUTTON_TEXT,
            "action_id": DEFAULT_ACTION_ID,
        },
        "timestamp": datetime.utcnow().isoformat(),
        "dismissible": True,
    }


def build_confirmation_widget(user_query: str, widget_id: str) -> dict[str, Any]:
    """Build confirmation widget data."""
    return {
        "id": widget_id,
        "type": "confirmation",
        "title": "Confirm Action",
        "content": None,
        "metadata": {
            "message": f"Please confirm: {user_query}",
            "confirm_label": DEFAULT_CONFIRM_LABEL,
            "cancel_label": DEFAULT_CANCEL_LABEL,
        },
        "timestamp": datetime.utcnow().isoformat(),
        "dismissible": True,
    }
