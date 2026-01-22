# =============================================================================
# AGENTX Widget Spawner - Interactive Widget Tools
# =============================================================================
# Interactive widgets: action, confirmation, image, gallery
# =============================================================================

import json
import uuid

from services.widget_spawner.builders import (
    build_action_widget,
    build_confirmation_widget,
    build_gallery_widget,
    build_image_widget,
)


def _generate_widget_id() -> str:
    """Generate unique widget ID."""
    return str(uuid.uuid4())


def create_action_widget(query: str, context: str = "") -> str:
    """Create an action widget for buttons, triggers, execute operations.

    Use for:
    - Buttons, actions, triggers
    - Execute operations, run commands
    """
    widget_data = build_action_widget(query, _generate_widget_id())
    return json.dumps({"widget": widget_data, "tool_used": "action"})


def create_confirmation_widget(query: str, context: str = "") -> str:
    """Create a confirmation widget for confirm dialogs, yes/no prompts.

    Use for:
    - Confirm dialogs, yes/no prompts
    - Approve/reject actions
    """
    widget_data = build_confirmation_widget(query, _generate_widget_id())
    return json.dumps({"widget": widget_data, "tool_used": "confirmation"})


def create_image_widget(query: str, context: str = "") -> str:
    """Create an image widget for pictures, photos, graphics.

    Use for:
    - Pictures, photos, graphics
    - Visual content, images
    """
    widget_data = build_image_widget(query, _generate_widget_id())
    return json.dumps({"widget": widget_data, "tool_used": "image"})


def create_gallery_widget(query: str, context: str = "") -> str:
    """Create a gallery widget for multiple images, photo collections.

    Use for:
    - Multiple images, image collection
    - Photo gallery, image grid
    """
    widget_data = build_gallery_widget(query, _generate_widget_id())
    return json.dumps({"widget": widget_data, "tool_used": "gallery"})
