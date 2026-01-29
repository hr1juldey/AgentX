"""Analyst agent wrapper for Real AgentX v0.1.

Ported from R014: services/pipeline/analyst.py

Wraps the dual-pass analyst node as a standalone agent.
Provides async interface for query analysis and data quality judgment.
"""

from __future__ import annotations

from typing import Any

from agentx.agent.nodes.analyst import analyst_node
from agentx.agent.state import AgentState
from agentx.core.dependencies import ensure_dspy_configured


# Global singleton instance
_analyst_agent_wrapper: AnalystAgentWrapper | None = None


class AnalystAgentWrapper:
    """Wrapper for the dual-pass analyst node.

    Provides a clean interface for running the analyst agent
    outside of the full LangGraph pipeline. Useful for testing
    and standalone analysis.
    """

    def __init__(self) -> None:
        """Initialize the analyst agent wrapper."""
        self._initialized = False

    async def analyze_query(
        self,
        query: str,
        session_id: str = "default",
    ) -> dict[str, Any]:
        """Run Pass 1 analysis on a user query.

        Args:
            query: User's question or request
            session_id: Optional session identifier

        Returns:
            dict with analysis results (query_type, domain, insights, etc.)
        """
        # Ensure DSPy is configured
        ensure_dspy_configured()

        # Create minimal state for Pass 1
        state: AgentState = {
            "messages": [],
            "ui": [],
            "reasoning_steps": 0,  # Triggers Pass 1
            "session_id": session_id,
            "total_tool_calls": 0,
        }

        # Run analyst node (Pass 1)
        result = await analyst_node(state)

        return result

    async def judge_data_quality(
        self,
        query: str,
        contextualized_data: dict[str, Any],
        session_id: str = "default",
    ) -> dict[str, Any]:
        """Run Pass 2 data quality judgment.

        Args:
            query: Original user query
            contextualized_data: Research data from contextualizer
            session_id: Optional session identifier

        Returns:
            dict with quality assessment (completeness, relevance, needs_more_research)
        """
        # Ensure DSPy is configured
        ensure_dspy_configured()

        # Create minimal state for Pass 2
        state: AgentState = {
            "messages": [],
            "ui": [],
            "reasoning_steps": 1,  # Triggers Pass 2
            "contextualized_data": contextualized_data,
            "session_id": session_id,
            "total_tool_calls": 0,
        }

        # Run analyst node (Pass 2)
        result = await analyst_node(state)

        return result

    async def run_full_analysis(
        self,
        query: str,
        contextualized_data: dict[str, Any] | None = None,
        session_id: str = "default",
    ) -> dict[str, Any]:
        """Run both Pass 1 and Pass 2 analysis.

        Args:
            query: User's question or request
            contextualized_data: Optional research data (triggers Pass 2 if provided)
            session_id: Optional session identifier

        Returns:
            dict with combined analysis results
        """
        # Run Pass 1 always
        pass1_result = await self.analyze_query(query, session_id)

        # Run Pass 2 if contextualized data provided
        if contextualized_data:
            pass2_result = await self.judge_data_quality(
                query, contextualized_data, session_id
            )
            return {
                "pass1": pass1_result,
                "pass2": pass2_result,
            }

        return {"pass1": pass1_result}


def get_analyst_agent() -> AnalystAgentWrapper:
    """Get the analyst agent wrapper singleton.

    Returns:
        AnalystAgentWrapper: The analyst agent wrapper instance.
    """
    ensure_dspy_configured()
    global _analyst_agent_wrapper
    if _analyst_agent_wrapper is None:
        _analyst_agent_wrapper = AnalystAgentWrapper()
    return _analyst_agent_wrapper
