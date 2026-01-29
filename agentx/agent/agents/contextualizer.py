"""Contextualizer agent wrapper for Real AgentX v0.1.

Ported from R014: services/pipeline/contextualizer.py

Wraps the contextualizer node as a standalone agent.
Provides async interface for context enrichment and injection.
"""

from __future__ import annotations

from typing import Any

from agentx.agent.nodes.contextualizer import contextualizer_node
from agentx.agent.state import AgentState
from agentx.core.dependencies import ensure_dspy_configured


# Global singleton instance
_contextualizer_agent_wrapper: ContextualizerAgentWrapper | None = None


class ContextualizerAgentWrapper:
    """Wrapper for the contextualizer node.

    Provides a clean interface for running the contextualizer agent
    outside of the full LangGraph pipeline. Useful for testing
    and standalone context enrichment.
    """

    def __init__(self) -> None:
        """Initialize the contextualizer agent wrapper."""
        self._initialized = False

    async def contextualize_findings(
        self,
        findings: str,
        citations: list[dict],
        user_query: str = "",
        session_id: str = "default",
    ) -> dict[str, Any]:
        """Contextualize research findings.

        Args:
            findings: Research findings to enrich
            citations: List of citation dicts for context
            user_query: Original user query
            session_id: Optional session identifier

        Returns:
            dict with contextualized findings and statistics
        """
        # Ensure DSPy is configured
        ensure_dspy_configured()

        # Create minimal state
        state: AgentState = {
            "messages": [],
            "ui": [],
            "reasoning_steps": 2,
            "session_id": session_id,
            "total_tool_calls": 0,
            "_research": {
                "findings": findings,
                "citations": citations,
            },
        }

        # Run contextualizer node
        result = await contextualizer_node(state)

        return result

    async def rerank_and_filter(
        self,
        context: list[dict],
        query: str,
        session_id: str = "default",
    ) -> dict[str, Any]:
        """Rerank and filter context chunks (shortcut method).

        Args:
            context: List of context chunks
            query: User query for relevance assessment
            session_id: Optional session identifier

        Returns:
            dict with reordered and filtered context
        """
        # Ensure DSPy is configured
        ensure_dspy_configured()

        # Create state with minimal research data
        state: AgentState = {
            "messages": [],
            "ui": [],
            "reasoning_steps": 2,
            "session_id": session_id,
            "total_tool_calls": 0,
            "_research": {
                "findings": "Findings",
                "citations": context,  # Use context as citations for processing
            },
        }

        # Run contextualizer node
        result = await contextualizer_node(state)

        return result


def get_contextualizer_agent() -> ContextualizerAgentWrapper:
    """Get the contextualizer agent wrapper singleton.

    Returns:
        ContextualizerAgentWrapper: The contextualizer agent wrapper instance.
    """
    ensure_dspy_configured()
    global _contextualizer_agent_wrapper
    if _contextualizer_agent_wrapper is None:
        _contextualizer_agent_wrapper = ContextualizerAgentWrapper()
    return _contextualizer_agent_wrapper
