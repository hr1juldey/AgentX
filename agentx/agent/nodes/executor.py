"""Executor node for Real AgentX v0.1.

Executes tools and generates responses.
"""

from typing import Any

from langchain_core.messages import AIMessage

from agentx.agent.state import AgentState


async def executor_node(state: AgentState) -> dict[str, Any]:
    """Execute tools and generate response.

    Args:
        state: Current agent state.

    Returns:
        dict: State updates with response message.
    """
    # Get the analysis from analyst node
    analysis = state.get("_analysis", {})
    tool_name = analysis.get("tool_name")

    # Get the latest message
    if not state["messages"]:
        return {"reasoning_steps": state["reasoning_steps"] + 1}

    latest_message = state["messages"][-1]
    query = latest_message.content

    # Execute tool if needed (placeholder)
    tool_result = None
    if tool_name and analysis.get("tool_needed"):
        # Would execute the actual tool here
        tool_result = f"Executed {tool_name}"

    # Generate response (placeholder - would use DSPy main agent)
    response = f"Processed: {query}"
    if tool_result:
        response += f"\n{tool_result}"

    # Create AI message
    message = AIMessage(content=response)

    return {
        "messages": [message],
        "reasoning_steps": state["reasoning_steps"] + 1,
        "total_tool_calls": state["total_tool_calls"] + (1 if tool_result else 0),
    }
}
