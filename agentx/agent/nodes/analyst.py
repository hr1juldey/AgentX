"""Analyst node for Real AgentX v0.1.

Analyzes user queries to extract intent and entities.
Following LangGraph node patterns from C003.
"""

from typing import Any

from agentx.agent.state import AgentState


async def analyst_node(state: AgentState) -> dict[str, Any]:
    """Analyze the user query to extract intent and entities.

    Args:
        state: Current agent state.

    Returns:
        dict: State updates with analysis results.
    """
    # Get the latest message
    if not state["messages"]:
        return {"reasoning_steps": state["reasoning_steps"] + 1}

    latest_message = state["messages"][-1]
    query = latest_message.content

    # Analyze query (placeholder - would use DSPy analyst agent)
    intent = "general_query"
    entities = []
    tool_needed = False
    tool_name = None

    # Simple keyword-based detection (would use LLM in production)
    if any(word in query.lower() for word in ["calculate", "math", "compute"]):
        intent = "calculation"
        tool_needed = True
        tool_name = "calculator"
    elif any(word in query.lower() for word in ["search", "find", "look up"]):
        intent = "web_search"
        tool_needed = True
        tool_name = "web_search"
    elif any(word in query.lower() for word in ["time", "clock", "date"]):
        intent = "get_time"
        tool_needed = True
        tool_name = "get_current_time"

    # Store analysis in state (for use by other nodes)
    return {
        "reasoning_steps": state["reasoning_steps"] + 1,
        "_analysis": {
            "intent": intent,
            "entities": entities,
            "tool_needed": tool_needed,
            "tool_name": tool_name,
        },
    }
