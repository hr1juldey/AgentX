"""POST endpoints for thread creation and invocation."""

from fastapi import HTTPException
from langchain_core.messages import HumanMessage

from agentx.agent.graph import get_graph  # type: ignore[import]
from agentx.agent.state import AgentState
from agentx.presentation.api.v1.threads.thread_manager import (
    create_thread_state,
    get_threads,
    serialize_state,
)


async def create_thread() -> dict:
    """Create a new thread.

    Returns:
        Thread info with thread_id
    """
    _threads = get_threads()
    thread_data = create_thread_state()
    thread_id = thread_data["thread_id"]
    _threads[thread_id] = thread_data

    return {
        "thread_id": thread_id,
        "created_at": thread_data["created_at"],
    }


async def invoke_thread(
    thread_id: str,
    input_data: dict,
) -> dict:
    """Execute graph once (non-streaming).

    Args:
        thread_id: Thread identifier
        input_data: Input data with messages field

    Returns:
        Final thread state
    """
    _threads = get_threads()

    if thread_id not in _threads:
        raise HTTPException(status_code=404, detail="Thread not found")

    thread = _threads[thread_id]
    graph = get_graph()

    # Prepare state
    initial_state: AgentState = {
        **thread["state"],
        "messages": thread["state"]["messages"].copy(),
    }

    # Add user message
    if "messages" in input_data:
        for msg in input_data["messages"]:
            if msg.get("role") == "user":
                initial_state["messages"] = [
                    *initial_state["messages"],
                    HumanMessage(content=msg["content"]),
                ]

    # Execute graph
    final_state = await graph.ainvoke(initial_state)

    # Update thread state
    thread["state"] = final_state  # type: ignore[assignment]
    from datetime import datetime, timezone

    thread["updated_at"] = datetime.now(timezone.utc).isoformat()

    return {
        "thread_id": thread_id,
        "values": serialize_state(final_state),
    }
