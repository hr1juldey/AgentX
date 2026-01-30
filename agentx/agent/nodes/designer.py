"""Designer node for LangGraph.

Ported from R014: services/pipeline/designer.py

**CRITICAL FIX**: STATE AWARE Designer agent.

This node checks `state.ui` for existing widgets before emitting new ones.
Fixes the R014 bug where the Designer sent the same widgets repeatedly.

Server-driven UI pattern from C007: push_ui_message() for widget emission.
"""

from typing import Any

from langchain_core.messages import AIMessage
from langgraph.graph.ui import push_ui_message  # type: ignore[import]

from agentx.agent.state import AgentState
from agentx.agent.tools.designer.color_scheme import ColorSchemeModule
from agentx.agent.tools.designer.hierarchy import HierarchyDesignerModule
from agentx.agent.tools.designer.pov_generator import POVGeneratorModule


async def designer_node(state: AgentState) -> dict[str, Any]:
    """Designer node: Select and emit UI widgets.

    **STATE AWARE**: Checks state.ui for existing widgets before emitting.

    Coordinates:
    - POV generator for widget selection
    - Color scheme for widget styling
    - Hierarchy designer for widget layout

    Args:
        state: Current agent state

    Returns:
        Updated state with UI widgets
    """
    # Get contextualized findings
    contextualized: dict[str, object] = state.get("contextualized_data", {})  # type: ignore[assignment]
    findings = str(contextualized.get("findings", ""))

    if not findings:
        return {
            "messages": [AIMessage(content="No findings to design widget for.")],
            "total_tool_calls": state.get("total_tool_calls", 0),
        }

    # **STATE AWARENESS**: Get existing widgets from state.ui
    existing_widgets = _get_existing_widget_types(state)

    # Get user query
    messages = state["messages"]
    user_query: str = ""
    for msg in reversed(messages):
        if hasattr(msg, "content") and isinstance(msg.content, str):
            user_query = msg.content
            break

    # Initialize modules
    pov_generator = POVGeneratorModule()
    color_scheme = ColorSchemeModule()
    hierarchy_designer = HierarchyDesignerModule()

    # Step 1: Generate point of view (widget recommendation)
    pov_result = pov_generator.forward(
        query=user_query,
        content=findings,
        existing_widgets=existing_widgets,
    )

    recommended_widget = pov_result["recommended_widget"]
    widget_props = pov_result["widget_props"]
    rationale = pov_result["rationale"]

    # Step 2: Design color scheme
    colors = color_scheme.forward(
        widget_type=recommended_widget,
        content_purpose="info",
    )

    # Step 3: Design hierarchy
    content_structure = str(widget_props.get("structure", "default"))
    hierarchy = hierarchy_designer.forward(
        widget_type=recommended_widget,
        content_structure=content_structure,
    )

    # Build final widget props with colors and hierarchy
    final_props: dict[str, object] = {
        **widget_props,
        "colors": colors,
        "hierarchy": hierarchy,
    }

    # Create designer message
    design_content = f"""Widget Design:

Recommended Widget: {recommended_widget}

Rationale:
{rationale}

Existing Widgets: {", ".join(existing_widgets) if existing_widgets else "none"}

This widget complements the existing UI without duplicating functionality.
"""

    message = AIMessage(content=design_content)

    # **EMIT WIDGET** using push_ui_message() for LangGraph server-driven UI
    # This adds the widget to state.ui, making it available to the frontend
    push_ui_message(
        recommended_widget,
        {
            "title": final_props.get("title", f"{recommended_widget.title()} Widget"),
            "content": final_props.get("content", ""),
            "colors": final_props.get("colors", {}),
            "hierarchy": final_props.get("hierarchy", {}),
            "rationale": rationale,
        },
        message=message,
    )

    return {
        "messages": [message],
        "_widget_design": {
            "widget_type": recommended_widget,
            "widget_props": final_props,
            "rationale": rationale,
            "existing_widgets": existing_widgets,
        },
        "total_tool_calls": state.get("total_tool_calls", 0) + 1,
    }


def _get_existing_widget_types(state: AgentState) -> list[str]:
    """**STATE AWARENESS**: Get list of existing widget types from state.ui.

    This is the critical fix that prevents duplicate widgets.
    The Designer can now see what widgets are already shown and select
    complementary widgets instead of repeating the same ones.

    Args:
        state: Current agent state

    Returns:
        list of existing widget type names
    """
    ui_messages = state.get("ui", [])
    existing_widgets = []

    for ui_msg in ui_messages:
        # ui_msg is AnyUIMessage from langgraph.graph.ui
        if hasattr(ui_msg, "name"):
            widget_name = str(ui_msg.name)
            existing_widgets.append(widget_name)

    return existing_widgets
