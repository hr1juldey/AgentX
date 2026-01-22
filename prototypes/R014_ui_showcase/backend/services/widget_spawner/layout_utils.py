# =============================================================================
# AGENTX Widget Spawner - Layout Utilities
# =============================================================================
# Position generation and layout utilities for intelligent UI placement.
# =============================================================================

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


def generate_positions(
    plan: Dict[str, Any], device_context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate suggested x, y positions for widgets.

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
        positioned_widgets = _generate_vertical_layout(
            widgets, screen_width, screen_height
        )
    elif layout == "grid_2column":
        positioned_widgets = _generate_grid_2column_layout(
            widgets, screen_width, screen_height
        )
    elif layout == "grid_3column":
        positioned_widgets = _generate_grid_3column_layout(
            widgets, screen_width, screen_height
        )
    elif layout == "masonry":
        positioned_widgets = _generate_masonry_layout(
            widgets, screen_width, screen_height
        )
    else:
        positioned_widgets = _generate_default_layout(
            widgets, screen_width, screen_height
        )

    return {**plan, "widgets": positioned_widgets}


def _generate_vertical_layout(
    widgets: List[Dict[str, Any]], screen_width: int, screen_height: int
) -> List[Dict[str, Any]]:
    """Stack widgets vertically with spacing."""
    positioned_widgets = []
    y_offset = 100
    widget_height = 350

    for widget in widgets:
        positioned_widgets.append(
            {
                **widget,
                "x": screen_width // 2 - 250,
                "y": y_offset,
            }
        )
        y_offset += widget_height + 50

    return positioned_widgets


def _generate_grid_2column_layout(
    widgets: List[Dict[str, Any]], screen_width: int, screen_height: int
) -> List[Dict[str, Any]]:
    """Two column grid layout."""
    positioned_widgets = []
    left_column = True
    y_offset = 100
    widget_height = 300

    for widget in widgets:
        if left_column:
            x = 100
        else:
            x = screen_width // 2 + 50

        positioned_widgets.append(
            {
                **widget,
                "x": x,
                "y": y_offset,
            }
        )

        if not left_column:
            y_offset += widget_height + 50

        left_column = not left_column

    return positioned_widgets


def _generate_grid_3column_layout(
    widgets: List[Dict[str, Any]], screen_width: int, screen_height: int
) -> List[Dict[str, Any]]:
    """Three column grid layout."""
    positioned_widgets = []
    column = 0
    y_offset = 100
    widget_height = 250

    column_width = screen_width // 3

    for widget in widgets:
        positioned_widgets.append(
            {
                **widget,
                "x": (column * column_width) + 50,
                "y": y_offset,
            }
        )

        column += 1
        if column >= 3:
            column = 0
            y_offset += widget_height + 50

    return positioned_widgets


def _generate_masonry_layout(
    widgets: List[Dict[str, Any]], screen_width: int, screen_height: int
) -> List[Dict[str, Any]]:
    """Masonry-style layout with varying heights."""
    positioned_widgets = []
    column_heights = [100, 100, 100]
    column_width = screen_width // 3

    for i, widget in enumerate(widgets):
        # Find shortest column
        shortest_col = min(range(3), key=lambda c: column_heights[c])

        # Vary widget height based on type
        widget_type = widget.get("type", "card")
        if widget_type == "chart":
            widget_height = 300
        elif widget_type == "markdown":
            widget_height = 200
        else:
            widget_height = 150

        positioned_widgets.append(
            {
                **widget,
                "x": (shortest_col * column_width) + 50,
                "y": column_heights[shortest_col],
            }
        )

        column_heights[shortest_col] += widget_height + 20

    return positioned_widgets


def _generate_default_layout(
    widgets: List[Dict[str, Any]], screen_width: int, screen_height: int
) -> List[Dict[str, Any]]:
    """Fallback layout - centered stack."""
    return _generate_vertical_layout(widgets, screen_width, screen_height)
