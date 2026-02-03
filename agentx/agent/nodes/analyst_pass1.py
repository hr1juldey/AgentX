"""Analyst Pass 1 implementation for LangGraph.

Pass 1: Understand query and context (before research).
"""

from typing import Any

from langchain_core.messages import AIMessage

from agentx.agent.state import AgentState
from agentx.agent.tools.analyst.context_analyzer import ContextAnalyzerModule
from agentx.agent.tools.analyst.goal_detector import GoalDetectorModule
from agentx.agent.tools.analyst.insight_extractor import InsightExtractorModule
from agentx.agent.tools.analyst.search_terms import SearchTermExtractorModule


async def pass_1_analysis(query: str, state: AgentState) -> dict[str, Any]:
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


__all__ = ["pass_1_analysis"]
