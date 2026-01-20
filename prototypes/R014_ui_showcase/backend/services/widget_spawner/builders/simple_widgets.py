# =============================================================================
# AGENTX Widget Spawner - Simple Widget Builders
# =============================================================================
# Helper functions for building simple widget data (no DSPy results)
# =============================================================================

import uuid
from datetime import datetime
from typing import Any

from services.widget_spawner.config import (
    DEFAULT_ACTION_BUTTON_TEXT,
    DEFAULT_ACTION_ID,
    DEFAULT_CANCEL_LABEL,
    DEFAULT_CONFIRM_LABEL,
    DEFAULT_GALLERY_IMAGE_HEIGHT,
    DEFAULT_GALLERY_IMAGE_WIDTH,
    DEFAULT_IMAGE_BASE_URL,
    DEFAULT_IMAGE_HEIGHT,
    DEFAULT_IMAGE_WIDTH,
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


def build_image_widget(user_query: str, widget_id: str) -> dict[str, Any]:
    """Build image widget data."""
    return {
        "id": widget_id,
        "type": "image",
        "title": "Generated Image",
        "content": f"Image for: {user_query}",
        "metadata": {
            "image_url": f"{DEFAULT_IMAGE_BASE_URL}/{DEFAULT_IMAGE_WIDTH}x{DEFAULT_IMAGE_HEIGHT}?random={uuid.uuid4().hex}"
        },
        "timestamp": datetime.utcnow().isoformat(),
        "dismissible": True,
    }


def build_gallery_widget(user_query: str, widget_id: str) -> dict[str, Any]:
    """Build gallery widget data."""
    return {
        "id": widget_id,
        "type": "gallery",
        "title": "Image Gallery",
        "content": f"Gallery for: {user_query}",
        "metadata": {
            "images": [
                {
                    "url": f"{DEFAULT_IMAGE_BASE_URL}/seed/{uuid.uuid4().hex}/{DEFAULT_GALLERY_IMAGE_WIDTH}x{DEFAULT_GALLERY_IMAGE_HEIGHT}",
                    "title": "Gallery Image 1",
                    "caption": "Generated image",
                },
                {
                    "url": f"{DEFAULT_IMAGE_BASE_URL}/seed/{uuid.uuid4().hex}/{DEFAULT_GALLERY_IMAGE_WIDTH}x{DEFAULT_GALLERY_IMAGE_HEIGHT}",
                    "title": "Gallery Image 2",
                    "caption": "Generated image",
                },
                {
                    "url": f"{DEFAULT_IMAGE_BASE_URL}/seed/{uuid.uuid4().hex}/{DEFAULT_GALLERY_IMAGE_WIDTH}x{DEFAULT_GALLERY_IMAGE_HEIGHT}",
                    "title": "Gallery Image 3",
                    "caption": "Generated image",
                },
                {
                    "url": f"{DEFAULT_IMAGE_BASE_URL}/seed/{uuid.uuid4().hex}/{DEFAULT_GALLERY_IMAGE_WIDTH}x{DEFAULT_GALLERY_IMAGE_HEIGHT}",
                    "title": "Gallery Image 4",
                    "caption": "Generated image",
                },
            ]
        },
        "timestamp": datetime.utcnow().isoformat(),
        "dismissible": True,
    }
