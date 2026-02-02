"""UI builder utilities for Designer node.

Handles state awareness and widget emission.
"""

from typing import Any

from langgraph.graph.ui import push_ui_message  # type: ignore[import]

from agentx.agent.state import AgentState


def get_existing_widget_types(state: AgentState) -> list[str]:
    """Get list of existing widget types from state.ui.

    **STATE AWARENESS**: This is the critical fix that prevents duplicate widgets.
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


def push_widget(
    recommended_widget: str,
    final_props: dict[str, Any],
    message,
) -> None:
    """Push widget to UI using LangGraph server-driven UI pattern.

    This adds the widget to state.ui, making it available to the frontend.

    Args:
        recommended_widget: The widget type to emit
        final_props: Widget properties
        message: AIMessage to associate with widget
    """
    push_ui_message(
        recommended_widget,
        {
            "title": final_props.get("title", f"{recommended_widget.title()} Widget"),
            "content": final_props.get("content", ""),
            "colors": final_props.get("colors", {}),
            "hierarchy": final_props.get("hierarchy", {}),
            "rationale": final_props.get("rationale", ""),
        },
        message=message,
    )
