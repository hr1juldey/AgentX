"""Analyst node for LangGraph.

Ported from R014: services/pipeline/analyst.py

Implements the dual-pass analyst pattern:
- Pass 1: Understand query and context (before research)
- Pass 2: Judge data quality and completeness (after contextualization)
"""

from typing import Any

from langchain_core.messages import AIMessage

from agentx.agent.state import AgentState
from agentx.agent.tools.analyst.context_analyzer import ContextAnalyzerModule
from agentx.agent.tools.analyst.data_quality_checker import DataQualityCheckerModule
from agentx.agent.tools.analyst.goal_detector import GoalDetectorModule
from agentx.agent.tools.analyst.insight_extractor import InsightExtractorModule
from agentx.agent.tools.analyst.search_terms import SearchTermExtractorModule


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
        return await _pass_1_analysis(user_message, state)
    else:
        # Pass 2: Data quality judgment
        contextualized_data = state.get("contextualized_data", {})
        return await _pass_2_judgment(user_message, contextualized_data, state)


async def _pass_1_analysis(query: str, state: AgentState) -> dict[str, Any]:
    """Pass 1: Analyze query and extract context.

    Args:
        query: User's question or request
        state: Current agent state

    Returns:
        dict with analysis results and a message
    """
    # Initialize modules
    context_analyzer = ContextAnalyzerModule()
    insight_extractor = InsightExtractorModule()
    goal_detector = GoalDetectorModule()
    search_term_extractor = SearchTermExtractorModule()

    # Run parallel context analysis
    context_result = context_analyzer(query=query)
    query_type = context_result["query_type"]
    domain = context_result["domain"]
    urgency = context_result["urgency"]

    # Extract insights
    insights_result = insight_extractor(query=query)
    insights = insights_result["insights"]

    # Detect goals and scope
    goal_result = goal_detector(query=query, insights=insights)
    goal = goal_result["goal"]
    scope = goal_result["scope"]
    depth = goal_result["depth"]

    # Extract search terms
    terms_result = search_term_extractor(query=query, insights=insights, domain=domain)
    search_terms = terms_result["search_terms"]

    # Create analysis message
    insight_lines = [f"- {insight}" for insight in insights[:5]]
    search_term_lines = [f"- {term}" for term in search_terms[:5]]

    analysis_content = f"""Query Analysis (Pass 1):

Query Type: {query_type}
Domain: {domain}
Urgency: {urgency}

Goal: {goal}
Scope: {scope}
Depth: {depth}

Key Insights:
{chr(10).join(insight_lines) if insight_lines else "- No insights extracted"}

Search Terms:
{chr(10).join(search_term_lines) if search_term_lines else "- No terms extracted"}
"""

    message = AIMessage(content=analysis_content)

    return {
        "messages": [message],
        "_analysis": {
            "query_type": query_type,
            "domain": domain,
            "urgency": urgency,
            "goal": goal,
            "scope": scope,
            "depth": depth,
            "insights": insights,
            "search_terms": search_terms,
        },
        "reasoning_steps": state.get("reasoning_steps", 0) + 1,
        "total_tool_calls": state.get("total_tool_calls", 0),
    }


async def _pass_2_judgment(
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
