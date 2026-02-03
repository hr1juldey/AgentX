"""Analyst Pass 2 implementation for LangGraph.

Pass 2: Judge data quality and completeness (after contextualization).
"""

from typing import Any

from langchain_core.messages import AIMessage

from agentx.agent.state import AgentState
from agentx.agent.tools.analyst.data_quality_checker import DataQualityCheckerModule


async def pass_2_judgment(
    query: str, contextualized_data: dict, state: AgentState
) -> dict[str, Any]:
    """Pass 2: Judge data quality and completeness.

    Args:
        query: Original user query
        contextualized_data: Research data from contextualizer
        state: Current agent state

    Returns:
        dict with quality assessment and a message
    """
    # Initialize module
    data_quality_checker = DataQualityCheckerModule()

    # Assess data quality
    quality_result = data_quality_checker(query=query, data=contextualized_data)

    completeness = quality_result["completeness_score"]
    relevance = quality_result["relevance_score"]
    missing = quality_result["missing_elements"]
    needs_more = quality_result["needs_more_research"]

    # Create judgment message
    missing_text = (
        f"Missing Elements: {missing}"
        if missing
        else "All required information available."
    )

    judgment_content = f"""Data Quality Assessment (Pass 2):

Completeness Score: {completeness:.2f}
Relevance Score: {relevance:.2f}
Needs More Research: {needs_more}

{missing_text}
"""

    message = AIMessage(content=judgment_content)

    return {
        "messages": [message],
        "_quality_assessment": {
            "completeness_score": completeness,
            "relevance_score": relevance,
            "missing_elements": missing,
            "needs_more_research": needs_more,
        },
        "reasoning_steps": state.get("reasoning_steps", 0) + 1,
        "total_tool_calls": state.get("total_tool_calls", 0),
    }


__all__ = ["pass_2_judgment"]
