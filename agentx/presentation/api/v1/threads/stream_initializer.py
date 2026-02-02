"""Stream initialization utilities for LangGraph threads.

Handles state preparation and graph compilation for streaming.
"""

from fastapi import HTTPException
from langchain_core.messages import HumanMessage, SystemMessage

from agentx.agent.graph import get_graph  # type: ignore[import]
from agentx.agent.state import AgentState
from agentx.presentation.api.v1.threads.thread_manager import get_threads


def prepare_stream_state(
    thread_id: str,
    input_data: dict,
) -> tuple[dict, AgentState, object]:
    """Prepare thread state and compiled graph for streaming.

    Args:
        thread_id: Thread identifier
        input_data: Input data for graph execution

    Returns:
        Tuple of (thread_dict, initial_state, compiled_graph)

    Raises:
        HTTPException: If thread not found
    """
    _threads = get_threads()

    if thread_id not in _threads:
        raise HTTPException(status_code=404, detail="Thread not found")

    thread = _threads[thread_id]
    graph = get_graph()

    # Compile the graph first to get CompiledStateGraph
    compiled_graph = graph.compile()

    # Prepare initial state
    initial_state: AgentState = {
        **thread["state"],
        "messages": thread["state"]["messages"].copy(),
    }

    # Add user message if provided
    if "messages" in input_data:
        for msg in input_data["messages"]:
            if msg.get("role") == "user":
                initial_state["messages"] = [
                    *initial_state["messages"],
                    HumanMessage(content=msg["content"]),
                ]
            elif msg.get("role") == "system":
                initial_state["messages"] = [
                    *initial_state["messages"],
                    SystemMessage(content=msg["content"]),
                ]

    return thread, initial_state, compiled_graph
