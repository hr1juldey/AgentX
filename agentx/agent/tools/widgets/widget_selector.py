"""Adaptive widget selection logic.

This module implements content-driven widget selection based on
accumulated research findings and query complexity.
"""

from typing import TYPE_CHECKING

import dspy

from agentx.agent.tools.widgets.widgets.creation import create_widgets
from agentx.agent.tools.widgets.widgets.detection import (
    DetectContentPatternModule,
    infer_widgets_from_patterns,
)
from agentx.agent.tools.widgets.widgets.filtering import apply_widget_filters
from agentx.agent.tools.widgets.widgets.node import select_widgets_node

if TYPE_CHECKING:
    pass


# Re-export signature for backward compatibility
from agentx.agent.tools.widgets.widgets.signatures import (  # noqa: F401
    DetectContentPatternSignature,
)


class WidgetSelectorModule(dspy.Module):
    """DSPy module for adaptive widget selection.

    Analyzes findings and selects relevant widgets based on:
    - Content patterns (comparison → table, temporal → timeline)
    - Query complexity (simple → 0-1 widgets, complex → 3-7 widgets)
    - Widget priority (highest first)
    """

    def __init__(self):
        """Initialize widget selector module."""
        super().__init__()
        self.detect_patterns = DetectContentPatternModule()

    def forward(
        self,
        query: str,
        research_findings: list[str],
        task_count: int,
    ) -> dspy.Prediction:
        """Select widgets based on findings and query complexity.

        Args:
            query: User's query
            research_findings: Accumulated research findings
            task_count: Number of tasks in execution plan

        Returns:
            dspy.Prediction: Selected widgets list
        """
        # Simple queries get 0 widgets
        if task_count == 0:
            return dspy.Prediction(
                selected_widgets=[],
                widget_count=0,
            )

        # Detect content patterns
        result = self.detect_patterns(query=query, research_findings=research_findings)

        # Parse suggested widgets
        import json

        widget_types: list[str] = []
        try:
            widget_types = json.loads(result.suggested_widgets)  # type: ignore[attr-defined]
        except (json.JSONDecodeError, ValueError):
            widget_types = infer_widgets_from_patterns(result)  # type: ignore[arg-type]

        # Map widget types with priority
        widgets = create_widgets(
            widget_types=widget_types,
            query=query,
            findings=research_findings,
            task_count=task_count,
        )

        # Sort by priority and apply limits
        widgets = apply_widget_filters(widgets, task_count)

        return dspy.Prediction(
            selected_widgets=widgets,
            widget_count=len(widgets),
        )


# Re-export node function for backward compatibility
select_widgets_node = select_widgets_node  # noqa: F811

__all__ = [
    "DetectContentPatternSignature",
    "WidgetSelectorModule",
    "select_widgets_node",
]
