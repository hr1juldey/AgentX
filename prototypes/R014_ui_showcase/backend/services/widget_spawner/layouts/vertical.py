# =============================================================================
# AGENTX Widget Spawner - Vertical Layout
# =============================================================================
# Vertical stacking layout for widgets
# =============================================================================

from typing import Any, Dict, List


def generate_vertical_layout(
    widgets: List[Dict[str, Any]], screen_width: int, screen_height: int
) -> List[Dict[str, Any]]:
    """Stack widgets vertically with spacing.

    Args:
        widgets: List of widget dicts to position
        screen_width: Screen width in pixels
        screen_height: Screen height in pixels

    Returns:
        List of widgets with x, y positions added
    """
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
