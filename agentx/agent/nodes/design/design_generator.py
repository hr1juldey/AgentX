"""Design generation logic for Designer node.

Handles widget selection, color scheme, and hierarchy design.
"""

from typing import Any

from langchain_core.messages import AIMessage

from agentx.agent.state import AgentState
from agentx.agent.tools.designer.color_scheme import ColorSchemeModule
from agentx.agent.tools.designer.hierarchy import HierarchyDesignerModule
from agentx.agent.tools.designer.pov_generator import POVGeneratorModule
from agentx.agent.nodes.design.ui_builder import get_existing_widget_types


def generate_design(state: AgentState) -> dict[str, Any]:
    """Generate UI widget design from findings.

    Coordinates:
    - POV generator for widget selection
    - Color scheme for widget styling
    - Hierarchy designer for widget layout

    Args:
        state: Current agent state

    Returns:
        Updated state with design metadata
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
    existing_widgets = get_existing_widget_types(state)

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
    pov_result = pov_generator(
        query=user_query,
        content=findings,
        existing_widgets=existing_widgets,
    )

    recommended_widget = pov_result["recommended_widget"]  # type: ignore[index]
    widget_props = pov_result["widget_props"]  # type: ignore[index]
    rationale = pov_result["rationale"]  # type: ignore[index]

    # Step 2: Design color scheme
    colors = color_scheme(  # type: ignore[index]
        widget_type=recommended_widget,
        content_purpose="info",
    )

    # Step 3: Design hierarchy
    content_structure = str(widget_props.get("structure", "default"))
    hierarchy = hierarchy_designer(  # type: ignore[index]
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

    return {
        "message": message,
        "recommended_widget": recommended_widget,
        "final_props": final_props,
        "rationale": rationale,
        "existing_widgets": existing_widgets,
    }
