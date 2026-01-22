# =============================================================================
# AGENTX Widget Spawner - Grid Layouts
# =============================================================================
# 2-column and 3-column grid layouts for widgets
# =============================================================================

from typing import Any, Dict, List


def generate_grid_2column_layout(
    widgets: List[Dict[str, Any]], screen_width: int, screen_height: int
) -> List[Dict[str, Any]]:
    """Two column grid layout.

    Args:
        widgets: List of widget dicts to position
        screen_width: Screen width in pixels
        screen_height: Screen height in pixels

    Returns:
        List of widgets with x, y positions added
    """
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


def generate_grid_3column_layout(
    widgets: List[Dict[str, Any]], screen_width: int, screen_height: int
) -> List[Dict[str, Any]]:
    """Three column grid layout.

    Args:
        widgets: List of widget dicts to position
        screen_width: Screen width in pixels
        screen_height: Screen height in pixels

    Returns:
        List of widgets with x, y positions added
    """
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
