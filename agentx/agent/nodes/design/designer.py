"""Designer node for LangGraph.

Ported from R014: services/pipeline/designer.py

**CRITICAL FIX**: STATE AWARE Designer agent.

This node checks `state.ui` for existing widgets before emitting new ones.
Fixes the R014 bug where the Designer sent the same widgets repeatedly.

Server-driven UI pattern from C007: push_ui_message() for widget emission.
"""

from typing import Any

from agentx.agent.nodes.design.design_generator import generate_design
from agentx.agent.nodes.design.ui_builder import push_widget
from agentx.agent.state import AgentState


async def designer_node(state: AgentState) -> dict[str, Any]:
    """Designer node: Select and emit UI widgets.

    **STATE AWARE**: Checks state.ui for existing widgets before emitting.

    Args:
        state: Current agent state

    Returns:
        Updated state with UI widgets
    """
    # Generate design
    design = generate_design(state)

    # Check if design was successful
    if "recommended_widget" not in design:
        return design

    # **EMIT WIDGET** using push_ui_message() for LangGraph server-driven UI
    push_widget(
        design["recommended_widget"],
        design["final_props"],
        design["message"],
    )

    return {
        "messages": [design["message"]],
        "_widget_design": {
            "widget_type": design["recommended_widget"],
            "widget_props": design["final_props"],
            "rationale": design["rationale"],
            "existing_widgets": design["existing_widgets"],
        },
        "total_tool_calls": state.get("total_tool_calls", 0) + 1,
    }
