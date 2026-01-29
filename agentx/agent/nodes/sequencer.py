"""Sequencer node for LangGraph.

Ported from R014: services/pipeline/sequencer.py

Orders and paces widgets for optimal user experience.
Implements staggered delivery pattern (0s, 2s, 3.5s, → 5s).
"""

from typing import Any

from langchain_core.messages import AIMessage

from agentx.agent.agents.delivery_planner import DeliveryPlanner
from agentx.agent.state import AgentState


async def sequencer_node(state: AgentState) -> dict[str, Any]:
    """Sequencer node: Order and pace widget delivery.

    Coordinates:
    - Delivery planner for staggered timing
    - Widget ordering for logical flow

    Args:
        state: Current agent state

    Returns:
        Updated state with widget sequence and timing
    """
    # Get widget selection from selector
    widget_selection = state.get("_widget_selection", {})
    selected_widget = widget_selection.get("widget_type", "card")

    # Get existing widgets
    existing_widgets = list(widget_selection.get("existing_widgets", []))  # type: ignore[arg-type]

    # Build widget list (existing + new)
    all_widgets = []
    for widget_type in existing_widgets:
        all_widgets.append({"type": widget_type, "purpose": "already shown"})

    if selected_widget:
        all_widgets.append(
            {
                "type": selected_widget,
                "purpose": "new selection",
            }
        )

    if not all_widgets:
        return {
            "messages": [AIMessage(content="No widgets to sequence.")],
            "total_tool_calls": state.get("total_tool_calls", 0),
        }

    # Get urgency from analysis
    analysis: dict[str, object] = state.get("_analysis", {})  # type: ignore[assignment]
    urgency = str(analysis.get("urgency", "routine"))

    # Initialize delivery planner
    delivery_planner = DeliveryPlanner()

    # Plan delivery schedule
    planned_widgets = delivery_planner.plan_delivery(all_widgets, urgency)

    # Calculate pacing info
    pacing = delivery_planner.calculate_pacing(len(all_widgets), urgency)

    # Create sequencer message
    sequencer_content = f"""Widget Sequencing:

Total Widgets: {len(all_widgets)}
Delivery Urgency: {urgency.upper()}

Delivery Schedule:
"""
    for i, widget in enumerate(planned_widgets):
        timing = widget["timing"]
        sequencer_content += (
            f"- Widget {i + 1}: {widget['type']} (delay: {timing['delay']}s)\n"
        )

    sequencer_content += f"""
Total Delivery Time: {pacing["total_time"]:.1f}s

Widgets are delivered with staggered timing for optimal user experience.
"""

    message = AIMessage(content=sequencer_content)

    return {
        "messages": [message],
        "_widget_sequence": {
            "widgets": planned_widgets,
            "pacing": pacing,
            "urgency": urgency,
        },
        "total_tool_calls": state.get("total_tool_calls", 0) + 1,
    }
