"""LangGraph node for widget selection.

Provides the node function for use in LangGraph workflows.
"""

from agentx.agent.tools.widgets.widget_selector import WidgetSelectorModule
from agentx.domain.models.graph_state import AgentState


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
