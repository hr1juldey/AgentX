"""Researcher agent wrapper for Real AgentX v0.1.

Ported from R014: services/pipeline/researcher.py

Wraps the researcher node as a standalone agent.
Provides async interface for web search and findings extraction.
"""

from __future__ import annotations

from typing import Any

from agentx.agent.nodes.researcher import researcher_node
from agentx.agent.state import AgentState
from agentx.core.dependencies import ensure_dspy_configured


# Global singleton instance
_researcher_agent_wrapper: ResearcherAgentWrapper | None = None


class ResearcherAgentWrapper:
    """Wrapper for the researcher node.

    Provides a clean interface for running the researcher agent
    outside of the full LangGraph pipeline. Useful for testing
    and standalone research operations.
    """

    def __init__(self) -> None:
        """Initialize the researcher agent wrapper."""
        self._initialized = False

    async def execute_research(
        self,
        search_terms: list[str],
        domain: str = "general",
        user_query: str = "",
        session_id: str = "default",
    ) -> dict[str, Any]:
        """Execute web search and extract findings.

        Args:
            search_terms: List of search terms from analyst
            domain: Subject domain for optimization
            user_query: Original user query for context
            session_id: Optional session identifier

        Returns:
            dict with research results (findings, citations, confidence)
        """
        # Ensure DSPy is configured
        ensure_dspy_configured()

        # Create minimal state
        state: AgentState = {
            "messages": [],
            "ui": [],
            "reasoning_steps": 1,
            "session_id": session_id,
            "total_tool_calls": 0,
            "_analysis": {
                "search_terms": search_terms,
                "domain": domain,
            },
        }

        # Run researcher node
        result = await researcher_node(state)

        return result

    async def search_and_structure(
        self,
        query: str,
        num_results: int = 10,
        domain: str = "general",
        session_id: str = "default",
    ) -> dict[str, Any]:
        """Execute a simple search query (shortcut method).

        Args:
            query: Search query
            num_results: Number of results to retrieve
            domain: Subject domain for optimization
            session_id: Optional session identifier

        Returns:
            dict with structured search results
        """
        # Ensure DSPy is configured
        ensure_dspy_configured()

        # Create state with single search term
        state: AgentState = {
            "messages": [],
            "ui": [],
            "reasoning_steps": 1,
            "session_id": session_id,
            "total_tool_calls": 0,
            "_analysis": {
                "search_terms": [query],
                "domain": domain,
            },
        }

        # Run researcher node
        result = await researcher_node(state)

        return result


def get_researcher_agent() -> ResearcherAgentWrapper:
    """Get the researcher agent wrapper singleton.

    Returns:
        ResearcherAgentWrapper: The researcher agent wrapper instance.
    """
    ensure_dspy_configured()
    global _researcher_agent_wrapper
    if _researcher_agent_wrapper is None:
        _researcher_agent_wrapper = ResearcherAgentWrapper()
    return _researcher_agent_wrapper
