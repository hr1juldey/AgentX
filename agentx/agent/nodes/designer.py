"""Designer node for LangGraph.

Ported from R014: services/pipeline/designer.py

**CRITICAL FIX**: STATE AWARE Designer agent.

This node checks `state.ui` for existing widgets before emitting new ones.
Fixes the R014 bug where the Designer sent the same widgets repeatedly.

Server-driven UI pattern from C007: push_ui_message() for widget emission.
"""

from typing import Any

from agentx.agent.nodes.design.designer import designer_node
from agentx.agent.state import AgentState


# Re-export for backward compatibility
async def designer_node_wrapper(state: AgentState) -> dict[str, Any]:
    """Wrapper for designer_node to maintain type compatibility."""
    return await designer_node(state)


def get_existing_widget_types(state: AgentState) -> list[str]:
    """Get existing widget types from state.

    Args:
        state: Current agent state

    Returns:
        list of existing widget type names
    """
    from agentx.agent.nodes.design.ui_builder import get_existing_widget_types as _get

    return _get(state)


# Alias for backward compatibility
designer_node_func = designer_node

__all__ = [
    "designer_node",
    "designer_node_func",
    "get_existing_widget_types",
]
