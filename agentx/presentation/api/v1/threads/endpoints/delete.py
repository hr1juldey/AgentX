"""DELETE endpoint for thread deletion."""

from fastapi import HTTPException

from agentx.presentation.api.v1.threads.thread_manager import get_threads


async def delete_thread(thread_id: str) -> dict:
    """Delete a thread.

    Args:
        thread_id: Thread identifier

    Returns:
        Deletion confirmation
    """
    _threads = get_threads()

    if thread_id not in _threads:
        raise HTTPException(status_code=404, detail="Thread not found")

    del _threads[thread_id]
    return {"deleted": True}
