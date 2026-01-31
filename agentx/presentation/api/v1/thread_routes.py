"""LangGraph thread routes for Real AgentX v0.1.

Implements LangGraph streaming API endpoints compatible with @langchain/langgraph-sdk.
Provides thread management, state queries, and streaming graph execution.

Endpoints:
- GET /api/v1/threads - Create thread
- GET /api/v1/threads/{thread_id} - Get thread state
- POST /api/v1/threads/{thread_id}/stream - Stream graph execution
- DELETE /api/v1/threads/{thread_id} - Delete thread
"""

from datetime import datetime
from typing import AsyncGenerator
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage, SystemMessage

from agentx.agent.graph import get_graph
from agentx.agent.state import AgentState


# In-memory thread storage (can be replaced with Redis/database later)
_threads: dict[str, dict] = {}


def _serialize_state(state: AgentState) -> dict:
    """Serialize AgentState to JSON-compatible dict.

    Args:
        state: AgentState to serialize

    Returns:
        JSON-compatible dict representation
    """
    return {
        "messages": [
            {
                "role": msg.type if hasattr(msg, "type") else "ai",
                "content": msg.content
                if isinstance(msg.content, str)
                else str(msg.content),
            }
            for msg in state.get("messages", [])
        ],
        "ui": state.get("ui", []),
        "session_id": state.get("session_id"),
        "reasoning_steps": state.get("reasoning_steps", 0),
        "total_tool_calls": state.get("total_tool_calls", 0),
        "contextualized_data": state.get("contextualized_data"),
        "values": state,  # Full state for LangGraph SDK compatibility
    }


def _generate_event(event_type: str, data: dict) -> str:
    """Generate SSE event string.

    Args:
        event_type: Event type (e.g., "messages/partial", "messages/complete")
        data: Event data

    Returns:
        SSE-formatted string
    """
    import json

    return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"


router = APIRouter(tags=["threads"])


@router.post("")
async def create_thread() -> dict:
    """Create a new thread.

    Returns:
        Thread info with thread_id
    """
    thread_id = str(uuid4())
    _threads[thread_id] = {
        "thread_id": thread_id,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "state": {
            "messages": [],
            "ui": [],
            "session_id": thread_id,
            "reasoning_steps": 0,
            "total_tool_calls": 0,
        },
    }

    return {
        "thread_id": thread_id,
        "created_at": _threads[thread_id]["created_at"],
    }


@router.get("/{thread_id}")
async def get_thread(thread_id: str) -> dict:
    """Get thread state.

    Args:
        thread_id: Thread identifier

    Returns:
        Thread state with values field for LangGraph SDK compatibility
    """
    if thread_id not in _threads:
        raise HTTPException(status_code=404, detail="Thread not found")

    thread = _threads[thread_id]
    return {
        "thread_id": thread_id,
        "created_at": thread["created_at"],
        "updated_at": thread["updated_at"],
        "values": _serialize_state(thread["state"]),
    }


@router.delete("/{thread_id}")
async def delete_thread(thread_id: str) -> dict:
    """Delete a thread.

    Args:
        thread_id: Thread identifier

    Returns:
        Deletion confirmation
    """
    if thread_id not in _threads:
        raise HTTPException(status_code=404, detail="Thread not found")

    del _threads[thread_id]
    return {"deleted": True}


async def _stream_graph_execution(
    thread_id: str,
    input_data: dict,
    config: dict | None = None,
) -> AsyncGenerator[str, None]:
    """Stream graph execution via SSE.

    Args:
        thread_id: Thread identifier
        input_data: Input data for graph execution
        config: Optional config for graph execution

    Yields:
        SSE event strings
    """
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

    # Stream the graph execution
    try:
        async for chunk in compiled_graph.astream(
            initial_state,
            config=config or {},
        ):
            # Update thread state
            if isinstance(chunk, dict):
                thread["state"].update(chunk)  # type: ignore[arg-type]

            # Send UI update events
            if isinstance(chunk, dict) and "ui" in chunk:
                for ui_msg in chunk.get("ui", []):
                    yield _generate_event(
                        "custom",
                        {
                            "name": ui_msg.get("name", "ui_component"),
                            "args": ui_msg,
                        },
                    )

            # Send message partial events
            if isinstance(chunk, dict) and "messages" in chunk:
                messages = chunk["messages"]
                if messages:
                    latest_msg = messages[-1]
                    if hasattr(latest_msg, "content"):
                        yield _generate_event(
                            "messages/partial",
                            {
                                "messages": [
                                    {
                                        "role": "assistant",
                                        "content": str(latest_msg.content),
                                    }
                                ]
                            },
                        )

        # Update thread metadata
        thread["updated_at"] = datetime.utcnow().isoformat()

        # Send completion event
        yield _generate_event(
            "messages/complete",
            {
                "messages": [
                    {
                        "role": msg.type if hasattr(msg, "type") else "ai",
                        "content": str(msg.content)
                        if hasattr(msg, "content")
                        else str(msg),
                    }
                    for msg in thread["state"].get("messages", [])
                ]
            },
        )

    except Exception as e:
        yield _generate_event(
            "error",
            {
                "error": str(e),
                "message": "Graph execution failed",
            },
        )


@router.get("/{thread_id}/stream")
async def stream_thread(
    thread_id: str,
) -> StreamingResponse:
    """Stream graph execution for a thread via SSE (GET).

    Args:
        thread_id: Thread identifier

    Returns:
        StreamingResponse with SSE events
    """
    if thread_id not in _threads:
        # Auto-create thread if it doesn't exist
        _threads[thread_id] = {
            "thread_id": thread_id,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "state": {
                "messages": [],
                "ui": [],
                "session_id": thread_id,
                "reasoning_steps": 0,
                "total_tool_calls": 0,
            },
        }

    return StreamingResponse(
        _stream_graph_execution(thread_id, {}),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/{thread_id}/invoke")
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
    thread["updated_at"] = datetime.utcnow().isoformat()

    return {
        "thread_id": thread_id,
        "values": _serialize_state(final_state),
    }
