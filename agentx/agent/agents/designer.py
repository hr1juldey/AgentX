"""Designer agent wrapper for Real AgentX v0.1.

Ported from R014: services/pipeline/designer.py

Wraps the STATE AWARE designer node as a standalone agent.
Provides async interface for UI widget design and selection.
"""

from __future__ import annotations

from typing import Any

from agentx.agent.nodes.designer import designer_node
from agentx.agent.state import AgentState
from agentx.core.dependencies import ensure_dspy_configured


# Global singleton instance
_designer_agent_wrapper: DesignerAgentWrapper | None = None


class DesignerAgentWrapper:
    """Wrapper for the STATE AWARE designer node.

    Provides a clean interface for running the designer agent
    outside of the full LangGraph pipeline. Useful for testing
    and standalone widget design.

    **STATE AWARE**: This wrapper maintains awareness of existing widgets
    to prevent duplicates (fixing the R014 bug).
    """

    def __init__(self) -> None:
        """Initialize the designer agent wrapper."""
        self._initialized = False

    async def design_widget(
        self,
        findings: str,
        existing_widgets: list[str],
        user_query: str = "",
        session_id: str = "default",
    ) -> dict[str, Any]:
        """Design a UI widget for findings.

        Args:
            findings: Research findings to present
            existing_widgets: List of already shown widget types (for state awareness)
            user_query: Original user query
            session_id: Optional session identifier

        Returns:
            dict with widget design (type, props, rationale)
        """
        # Ensure DSPy is configured
        ensure_dspy_configured()

        # Create minimal state
        state: AgentState = {
            "messages": [],
            "ui": [],  # Empty UI for standalone usage
            "reasoning_steps": 3,
            "session_id": session_id,
            "total_tool_calls": 0,
            "contextualized_data": {
                "findings": findings,
            },
        }

        # Run designer node
        result = await designer_node(state)

        return result

    async def recommend_widget(
        self,
        content: str,
        query: str,
        existing_ui: list[str],
        session_id: str = "default",
    ) -> dict[str, Any]:
        """Get widget recommendation without full design (shortcut method).

        Args:
            content: Content to present
            query: User query
            existing_ui: List of existing widget types
            session_id: Optional session identifier

        Returns:
            dict with widget recommendation
        """
        # Ensure DSPy is configured
        ensure_dspy_configured()

        # Create state with findings
        state: AgentState = {
            "messages": [],
            "ui": [],
            "reasoning_steps": 3,
            "session_id": session_id,
            "total_tool_calls": 0,
            "contextualized_data": {
                "findings": content,
            },
        }

        # Run designer node
        result = await designer_node(state)

        return result


def get_designer_agent() -> DesignerAgentWrapper:
    """Get the designer agent wrapper singleton.

    Returns:
        DesignerAgentWrapper: The designer agent wrapper instance.
    """
    ensure_dspy_configured()
    global _designer_agent_wrapper
    if _designer_agent_wrapper is None:
        _designer_agent_wrapper = DesignerAgentWrapper()
    return _designer_agent_wrapper
