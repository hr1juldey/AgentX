"""Thread management API endpoints."""

from fastapi import APIRouter

router = APIRouter(prefix="/threads", tags=["threads"])


@router.post("/{thread_id}")
async def create_thread(thread_id: str) -> dict:
    """Create a new thread.

    Args:
        thread_id: Thread identifier

    Returns:
        Thread creation result

    Raises:
        NotImplementedError: If not yet implemented
    """
    raise NotImplementedError("POST /threads/{id} not yet implemented")


@router.get("/{thread_id}/history")
async def get_thread_history(thread_id: str, limit: int = 20) -> dict:
    """Get thread history.

    Args:
        thread_id: Thread identifier
        limit: Maximum messages to return

    Returns:
        Thread history

    Raises:
        NotImplementedError: If not yet implemented
    """
    raise NotImplementedError("GET /threads/{id}/history not yet implemented")
