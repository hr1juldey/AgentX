"""Widget Selector agent wrapper for Real AgentX v0.1.

Ported from R014: services/pipeline/widget_selector.py

Wraps the widget selector node as a standalone agent.
Provides async interface for widget selection (hybrid rule + LLM).
"""

from __future__ import annotations

from typing import Any

from agentx.agent.nodes.widget_selector import widget_selector_node
from agentx.agent.state import AgentState
from agentx.core.dependencies import ensure_dspy_configured


# Global singleton instance
_widget_selector_agent_wrapper: WidgetSelectorAgentWrapper | None = None


class WidgetSelectorAgentWrapper:
    """Wrapper for the widget selector node.

    Provides a clean interface for running the widget selector agent
    outside of the full LangGraph pipeline. Useful for testing
    and standalone widget selection.

    Uses hybrid approach: rule-based for fast path, LLM for complex cases.
    """

    def __init__(self) -> None:
        """Initialize the widget selector agent wrapper."""
        self._initialized = False

    async def select_widget(
        self,
        findings: str,
        existing_widgets: list[str],
        user_query: str = "",
        session_id: str = "default",
    ) -> dict[str, Any]:
        """Select appropriate widget for findings.

        Args:
            findings: Research findings to present
            existing_widgets: List of already shown widget types
            user_query: Original user query
            session_id: Optional session identifier

        Returns:
            dict with widget selection (type, confidence, reasoning)
        """
        # Ensure DSPy is configured
        ensure_dspy_configured()

        # Create minimal state
        state: AgentState = {
            "messages": [],
            "ui": [],
            "reasoning_steps": 4,
            "session_id": session_id,
            "total_tool_calls": 0,
            "contextualized_data": {
                "findings": findings,
            },
            "_widget_design": {
                "existing_widgets": existing_widgets,
            },
        }

        # Run widget selector node
        result = await widget_selector_node(state)

        return result

    async def match_widget(
        self,
        content_type: str,
        query: str,
        existing_ui: list[str],
        session_id: str = "default",
    ) -> dict[str, Any]:
        """Get widget match using hybrid selection (shortcut method).

        Args:
            content_type: Type of content to present
            query: User query
            existing_ui: List of existing widget types
            session_id: Optional session identifier

        Returns:
            dict with widget match result
        """
        # Ensure DSPy is configured
        ensure_dspy_configured()

        # Create state with findings
        state: AgentState = {
            "messages": [],
            "ui": [],
            "reasoning_steps": 4,
            "session_id": session_id,
            "total_tool_calls": 0,
            "contextualized_data": {
                "findings": f"Content of type: {content_type}",
            },
            "_widget_design": {
                "existing_widgets": existing_ui,
            },
        }

        # Run widget selector node
        result = await widget_selector_node(state)

        return result


def get_widget_selector_agent() -> WidgetSelectorAgentWrapper:
    """Get the widget selector agent wrapper singleton.

    Returns:
        WidgetSelectorAgentWrapper: The widget selector agent wrapper instance.
    """
    ensure_dspy_configured()
    global _widget_selector_agent_wrapper
    if _widget_selector_agent_wrapper is None:
        _widget_selector_agent_wrapper = WidgetSelectorAgentWrapper()
    return _widget_selector_agent_wrapper
