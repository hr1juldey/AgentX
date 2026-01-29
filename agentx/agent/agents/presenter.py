"""Presenter agent wrapper for Real AgentX v0.1.

Ported from R014: services/pipeline/presenter.py

Wraps the presenter node as a standalone agent.
Presents findings with quality check (final pipeline node).
"""

from __future__ import annotations

from typing import Any

from agentx.agent.nodes.presenter import presenter_node
from agentx.agent.state import AgentState
from agentx.core.dependencies import ensure_dspy_configured


# Global singleton instance
_presenter_agent_wrapper: PresenterAgentWrapper | None = None


class PresenterAgentWrapper:
    """Wrapper for the presenter node.

    Provides a clean interface for running the presenter agent
    outside of the full LangGraph pipeline.

    Final node in the 7-pipeline sequence.
    """

    def __init__(self) -> None:
        """Initialize the presenter agent wrapper."""
        self._initialized = False

    async def present_findings(
        self,
        findings: str,
        user_query: str = "",
        session_id: str = "default",
    ) -> dict[str, Any]:
        """Present findings with quality check.

        Args:
            findings: Research findings to present
            user_query: Original user query
            session_id: Optional session identifier

        Returns:
            dict with final presentation and quality score
        """
        # Ensure DSPy is configured
        ensure_dspy_configured()

        # Create minimal state
        state: AgentState = {
            "messages": [],
            "ui": [],
            "reasoning_steps": 6,
            "session_id": session_id,
            "total_tool_calls": 0,
            "contextualized_data": {
                "findings": findings,
            },
        }

        # Run presenter node
        result = await presenter_node(state)

        return result


def get_presenter_agent() -> PresenterAgentWrapper:
    """Get the presenter agent wrapper singleton.

    Returns:
        PresenterAgentWrapper: The presenter agent wrapper instance.
    """
    ensure_dspy_configured()
    global _presenter_agent_wrapper
    if _presenter_agent_wrapper is None:
        _presenter_agent_wrapper = PresenterAgentWrapper()
    return _presenter_agent_wrapper
