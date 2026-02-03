"""Analyst node for LangGraph.

Ported from R014: services/pipeline/analyst.py

Implements the dual-pass analyst pattern:
- Pass 1: Understand query and context (before research)
- Pass 2: Judge data quality and completeness (after contextualization)
"""

from typing import Any

from agentx.agent.nodes.analyst_passes import pass_1_analysis, pass_2_judgment
from agentx.agent.state import AgentState


async def analyst_node(state: AgentState) -> dict[str, Any]:
    """Analyst node: Analyzes query and judges data quality.

    Dual-pass implementation:
    - Pass 1: Understand query and extract insights/terms
    - Pass 2: Assess data quality and completeness

    Args:
        state: Current agent state

    Returns:
        Updated state with analysis results
    """
    # Get the last user message
    messages = state["messages"]
    user_message = None
    for msg in reversed(messages):
        if hasattr(msg, "content") and msg.content:
            user_message = msg.content
            break

    if not user_message:
        return {"reasoning_steps": state["reasoning_steps"] + 1}

    # Determine pass number from state
    # Pass 1: Initial analysis (before researcher)
    # Pass 2: Data quality judgment (after contextualizer)
    reasoning_steps = state.get("reasoning_steps", 0)

    if reasoning_steps == 0:
        # Pass 1: Initial analysis
        return await pass_1_analysis(user_message, state)
    else:
        # Pass 2: Data quality judgment
        contextualized_data = state.get("contextualized_data", {})
        return await pass_2_judgment(user_message, contextualized_data, state)


__all__ = ["analyst_node"]
