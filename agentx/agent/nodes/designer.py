"""Designer node for Real AgentX v0.1.

Selects UI components with state awareness (C007 key feature).
The designer can see existing widgets via state.ui to avoid duplicates.
"""

from typing import Any

from langgraph.graph.ui import push_ui_message
from langchain_core.messages import AIMessage

from agentx.agent.state import AgentState


async def designer_node(state: AgentState) -> dict[str, Any]:
    """Select UI components based on query and existing widgets.

    State awareness: Checks state.ui to avoid duplicate widgets.
    This solves R014's problem where designer sent same widgets repeatedly.

    Args:
        state: Current agent state (includes ui field with all shown widgets).

    Returns:
        dict: State updates with new UI components.
    """
    # Get the analysis from analyst node
    analysis = state.get("_analysis", {})
    intent = analysis.get("intent", "general_query")

    # State awareness: Check what widgets are already shown
    existing_widgets = [msg.name for msg in state.get("ui", [])]

    # Get the latest message
    if not state["messages"]:
        return {"reasoning_steps": state["reasoning_steps"] + 1}

    latest_message = state["messages"][-1]
    response = latest_message.content

    # Select appropriate widget based on intent and existing widgets
    # This is where state awareness prevents duplicates!

    widget_type = "markdown"  # Default
    widget_props: dict[str, Any] = {}

    if intent == "calculation" and "card" not in existing_widgets:
        widget_type = "card"
        widget_props = {
            "title": "Calculation Result",
            "content": response,
        }
    elif intent == "web_search" and "searchResult" not in existing_widgets:
        widget_type = "searchResult"
        widget_props = {
            "query": analysis.get("entities", [""])[0] if analysis.get("entities") else response,
            "results": [],  # Would be populated from search tool
        }
    elif intent == "get_time" and "card" not in existing_widgets:
        widget_type = "card"
        widget_props = {
            "title": "Current Time",
            "content": response,
        }
    else:
        # Default to markdown if widget already shown
        widget_type = "markdown"
        widget_props = {"content": response}

    # Emit UI component via push_ui_message (C007 pattern)
    # The ui_message_reducer automatically adds this to state.ui
    push_ui_message(
        widget_type,
        widget_props,
        message=AIMessage(content=f"Displaying {widget_type} widget"),
    )

    return {
        "reasoning_steps": state["reasoning_steps"] + 1,
    }
