"""Adaptive widget selection logic.

This module implements content-driven widget selection based on
accumulated research findings and query complexity.
"""

from typing import TYPE_CHECKING

import dspy

from agentx.domain.models.graph_state import AgentState
from agentx.domain.models.widget_selection import (
    WidgetSpecification,
    WidgetType,
)

if TYPE_CHECKING:
    pass


class DetectContentPatternSignature(dspy.Signature):
    """Signature for detecting content patterns in findings.

    The LLM analyzes research findings and identifies patterns
    that map to specific widget types.
    """

    query = dspy.InputField(desc="User's original query")
    research_findings = dspy.InputField(desc="Accumulated research findings")

    has_comparison = dspy.OutputField(desc="True if comparing items")
    has_temporal_data = dspy.OutputField(desc="True if time-series data")
    has_geographic_data = dspy.OutputField(desc="True if location-based data")
    has_ranking = dspy.OutputField(desc="True if ranked items")
    suggested_widgets = dspy.OutputField(
        desc="JSON string of widget types: ['data_table', 'chart', etc.]"
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
        self.detect_patterns = dspy.Predict(DetectContentPatternSignature)

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

        findings_text = "\n".join(f"- {f}" for f in research_findings)

        # Detect content patterns
        result = self.detect_patterns(
            query=query,
            research_findings=findings_text,
        )

        # Parse suggested widgets
        import json

        widget_types: list[str] = []
        try:
            widget_types = json.loads(result.suggested_widgets)  # type: ignore[attr-defined]
        except (json.JSONDecodeError, ValueError):
            widget_types = self._infer_widgets_from_patterns(result)  # type: ignore[arg-type]

        # Map widget types with priority
        widgets = self._create_widgets(
            widget_types=widget_types,
            query=query,
            findings=research_findings,
            task_count=task_count,
        )

        # Sort by priority and apply limits
        widgets.sort(key=lambda w: w.priority, reverse=True)

        # Apply widget count limits based on task count
        max_widgets = self._get_max_widget_count(task_count)
        widgets = widgets[:max_widgets]

        return dspy.Prediction(
            selected_widgets=widgets,
            widget_count=len(widgets),
        )

    def _infer_widgets_from_patterns(self, result: dspy.Prediction) -> list[str]:
        """Infer widget types from detected patterns.

        Args:
            result: Pattern detection result

        Returns:
            list[str]: Suggested widget types
        """
        widget_types = []

        # Map patterns to widgets
        if result.has_comparison.lower() == "true":  # type: ignore[attr-defined]
            widget_types.append("data_table")

        if result.has_temporal_data.lower() == "true":  # type: ignore[attr-defined]
            widget_types.append("timeline")
            widget_types.append("chart")

        if result.has_geographic_data.lower() == "true":  # type: ignore[attr-defined]
            widget_types.append("map")

        if result.has_ranking.lower() == "true":  # type: ignore[attr-defined]
            widget_types.append("data_table")

        # Default: text card
        if not widget_types:
            widget_types.append("text_card")

        return widget_types

    def _create_widgets(
        self,
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

    def _get_max_widget_count(self, task_count: int) -> int:
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


def select_widgets_node(state: AgentState) -> dict:
    """Select widgets based on accumulated findings.

    Args:
        state: Current agent state

    Returns:
        dict: Updated state with selected_widgets
    """
    query = state["query"]
    findings = state.get("research_findings", [])
    plan = state.get("execution_plan")
    task_count = len(plan.research_tasks) if plan else 0

    # Skip if no findings
    if not findings:
        return {"selected_widgets": [], "widget_count": 0}

    # Select widgets using DSPy module
    selector = WidgetSelectorModule()
    prediction = selector(
        query=query,
        research_findings=findings,
        task_count=task_count,
    )

    return {
        "selected_widgets": prediction.selected_widgets,  # type: ignore[attr-defined]
        "widget_count": prediction.widget_count,  # type: ignore[attr-defined]
        "execution_path": ["widget_selector"],
    }
