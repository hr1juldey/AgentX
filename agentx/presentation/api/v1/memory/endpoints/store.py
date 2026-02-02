"""Store endpoint for memory routes.

POST /store - Store a memory with temporal metadata.
"""

from uuid import UUID

from fastapi import status

from agentx.application.dtos.memory_dtos import (
    StoreMemoryRequest,
    StoreMemoryResponse,
)
from agentx.presentation.api.v1.memory.dependencies import get_store_use_case


async def store_memory(request: StoreMemoryRequest) -> StoreMemoryResponse:
    """Store a memory with temporal metadata.

    Args:
        request: Store memory request.

    Returns:
        StoreMemoryResponse: Stored memory details.
    """
    use_case = get_store_use_case()

    session_id = UUID(request.sessionId) if request.sessionId else None

    result = await use_case.execute(
        content=request.content,
        user_id=request.userId,
        temporal_type=request.temporalType,
        tier=request.tier,
        session_id=session_id,
        metadata=request.metadata,
    )

    return StoreMemoryResponse(**result)


# Configure endpoint for router
store_endpoint_config = {
    "path": "/store",
    "response_model": StoreMemoryResponse,
    "status_code": status.HTTP_201_CREATED,
}
