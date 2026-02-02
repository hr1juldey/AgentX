"""Filtering logic for widget selection.

Handles widget count limits and priority sorting.
"""

from agentx.domain.models.widget_selection import WidgetSpecification


def get_max_widget_count(task_count: int) -> int:
    """Get max widget count based on task count.

    Args:
        task_count: Number of tasks in execution plan

    Returns:
        int: Maximum widgets to display
    """
    if task_count == 0:
        return 0
    elif task_count <= 2:
        return 2
    elif task_count <= 5:
        return 4
    else:
        return 7


def apply_widget_filters(
    widgets: list[WidgetSpecification],
    task_count: int,
) -> list[WidgetSpecification]:
    """Apply priority sorting and count limits.

    Args:
        widgets: List of widget specifications
        task_count: Number of tasks for limit calculation

    Returns:
        list[WidgetSpecification]: Filtered widgets
    """
    # Sort by priority (highest first)
    widgets.sort(key=lambda w: w.priority, reverse=True)

    # Apply widget count limits based on task count
    max_widgets = get_max_widget_count(task_count)
    return widgets[:max_widgets]
