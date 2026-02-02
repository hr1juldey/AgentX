"""GET endpoints for thread retrieval and streaming."""

from fastapi import HTTPException
from fastapi.responses import StreamingResponse

from agentx.presentation.api.v1.threads.thread_manager import (
    create_thread_state,
    get_threads,
    serialize_state,
)
from agentx.presentation.api.v1.threads.thread_streaming import (
    stream_graph_execution,
)


async def get_thread(thread_id: str) -> dict:
    """Get thread state.

    Args:
        thread_id: Thread identifier

    Returns:
        Thread state with values field for LangGraph SDK compatibility
    """
    _threads = get_threads()

    if thread_id not in _threads:
        raise HTTPException(status_code=404, detail="Thread not found")

    thread = _threads[thread_id]
    return {
        "thread_id": thread_id,
        "created_at": thread["created_at"],
        "updated_at": thread["updated_at"],
        "values": serialize_state(thread["state"]),
    }


async def stream_thread(
    thread_id: str,
) -> StreamingResponse:
    """Stream graph execution for a thread via SSE (GET).

    Args:
        thread_id: Thread identifier

    Returns:
        StreamingResponse with SSE events
    """
    _threads = get_threads()

    if thread_id not in _threads:
        # Auto-create thread if it doesn't exist
        _threads[thread_id] = create_thread_state(thread_id)

    return StreamingResponse(
        stream_graph_execution(thread_id, {}),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
