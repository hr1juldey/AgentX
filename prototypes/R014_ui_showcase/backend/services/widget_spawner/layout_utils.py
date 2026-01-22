# =============================================================================
# AGENTX Widget Spawner - Layout Utilities
# =============================================================================
# Position generation and layout utilities for intelligent UI placement.
# =============================================================================

import logging
from typing import Any, Dict

from services.widget_spawner.layouts import (
    generate_default_layout,
    generate_grid_2column_layout,
    generate_grid_3column_layout,
    generate_masonry_layout,
    generate_vertical_layout,
)

logger = logging.getLogger(__name__)


def generate_positions(
    plan: Dict[str, Any], device_context: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate suggested x, y positions for widgets.

    Frontend can use these OR override with its own layout.

    Args:
        plan: Presentation plan with layout type and widgets
        device_context: Device info (type, screen_width, screen_height)

    Returns:
        Updated plan with x, y positions added to widgets
    """
    screen_width = device_context.get("screen_width", 1920)
    screen_height = device_context.get("screen_height", 1080)

    widgets = plan.get("widgets", [])
    layout = plan.get("layout", "simple_vertical")

    if layout == "simple_vertical":
        positioned_widgets = generate_vertical_layout(
            widgets, screen_width, screen_height
        )
    elif layout == "grid_2column":
        positioned_widgets = generate_grid_2column_layout(
            widgets, screen_width, screen_height
        )
    elif layout == "grid_3column":
        positioned_widgets = generate_grid_3column_layout(
            widgets, screen_width, screen_height
        )
    elif layout == "masonry":
        positioned_widgets = generate_masonry_layout(
            widgets, screen_width, screen_height
        )
    else:
        positioned_widgets = generate_default_layout(
            widgets, screen_width, screen_height
        )

    return {**plan, "widgets": positioned_widgets}
