"""Thread routes facade for Real AgentX v0.1.

This is a facade that re-exports the router from split components.
All endpoint implementations are in the endpoints/ subdirectory.
"""

from fastapi import APIRouter

from agentx.presentation.api.v1.threads.endpoints import (
    create_thread,
    delete_thread,
    get_thread,
    invoke_thread,
    stream_thread,
)


router = APIRouter(tags=["threads"])


# POST endpoints
router.post("", name="create_thread")(create_thread)
router.post("/{thread_id}/invoke", name="invoke_thread")(invoke_thread)


# GET endpoints
router.get("/{thread_id}", name="get_thread")(get_thread)
router.get("/{thread_id}/stream", name="stream_thread")(stream_thread)


# DELETE endpoints
router.delete("/{thread_id}", name="delete_thread")(delete_thread)


__all__ = ["router"]
