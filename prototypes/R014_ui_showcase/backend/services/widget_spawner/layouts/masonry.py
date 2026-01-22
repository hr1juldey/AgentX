# =============================================================================
# AGENTX Widget Spawner - Masonry Layout
# =============================================================================
# Masonry-style layout with varying heights for widgets
# =============================================================================

from typing import Any, Dict, List


def generate_masonry_layout(
    widgets: List[Dict[str, Any]], screen_width: int, screen_height: int
) -> List[Dict[str, Any]]:
    """Masonry-style layout with varying heights.

    Args:
        widgets: List of widget dicts to position
        screen_width: Screen width in pixels
        screen_height: Screen height in pixels

    Returns:
        List of widgets with x, y positions added
    """
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


def generate_default_layout(
    widgets: List[Dict[str, Any]], screen_width: int, screen_height: int
) -> List[Dict[str, Any]]:
    """Fallback layout - centered stack.

    Args:
        widgets: List of widget dicts to position
        screen_width: Screen width in pixels
        screen_height: Screen height in pixels

    Returns:
        List of widgets with x, y positions added
    """
    # Import here to avoid circular dependency
    from services.widget_spawner.layouts.vertical import generate_vertical_layout

    return generate_vertical_layout(widgets, screen_width, screen_height)
