"""Widget creation for widget selection.

Creates widget specifications from detected types.
"""

from agentx.domain.models.widget_selection import (
    WidgetSpecification,
    WidgetType,
)


def create_widgets(
    widget_types: list[str],
    query: str,
    findings: list[str],
    task_count: int,
) -> list[WidgetSpecification]:
    """Create widget specifications.

    Args:
        widget_types: List of widget type names
        query: User query
        findings: Research findings
        task_count: Task count for priority

    Returns:
        list[WidgetSpecification]: Widget specifications
    """
    widgets = []

    for i, widget_type in enumerate(widget_types):
        # Map string to enum
        try:
            wt = WidgetType(widget_type)
        except ValueError:
            wt = WidgetType.TEXT_CARD

        # Priority based on position and task count
        priority = 10 - i  # Earlier = higher priority

        widget = WidgetSpecification(
            widget_type=wt,
            title=f"{query[:50]}...",
            content={
                "findings": findings[:3],  # Top 3 findings
            },
            priority=priority,
            sources=[f"source_{i}"],
        )
        widgets.append(widget)

    return widgets
