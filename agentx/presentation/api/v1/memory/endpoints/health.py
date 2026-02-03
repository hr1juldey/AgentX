"""Health and active states endpoints for memory routes.

GET /health - Health check for memory services.
GET /active-states/{user_id} - Get active duration states.
"""

from datetime import datetime
from typing import Any

from agentx.application.dtos.memory_dtos import HealthResponse
from agentx.core.dependencies import get_vector_store
from agentx.presentation.api.v1.memory.dependencies import get_duration_service


async def health_check() -> HealthResponse:
    """Health check for memory services.

    Returns:
        HealthResponse: Health status.
    """
    # Check Qdrant connection
    qdrant_connected = True
    try:
        store = get_vector_store()
        store.client.get_collections()
    except Exception:
        qdrant_connected = False

    return HealthResponse(
        status="healthy" if qdrant_connected else "unhealthy",
        qdrant_connected=qdrant_connected,
        timestamp=datetime.now().isoformat(),
    )


async def get_active_states(user_id: str) -> dict[str, Any]:
    """Get active duration states for a user.

    Args:
        user_id: User identifier.

    Returns:
        dict: Active states summary.
    """
    svc = get_duration_service()
    summary = svc.get_duration_summary()

    return {
        "user_id": user_id,
        "active_states": summary["active_states"],
        "tracked_entities": summary["tracked_entities"],
        "timestamp": summary["timestamp"],
    }


# Configure endpoints for router
health_endpoint_config = {
    "path": "/health",
    "response_model": HealthResponse,
}

active_states_endpoint_config = {
    "path": "/active-states/{user_id}",
}
