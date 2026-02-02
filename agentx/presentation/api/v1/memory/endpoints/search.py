"""Search endpoint for memory routes.

POST /search - Search memories with temporal filtering.
"""

from uuid import UUID

from agentx.application.dtos.memory_dtos import (
    SearchMemoryRequest,
    SearchMemoryResponse,
)
from agentx.presentation.api.v1.memory.dependencies import get_search_use_case


async def search_memory(request: SearchMemoryRequest) -> SearchMemoryResponse:
    """Search memories with temporal filtering.

    Args:
        request: Search memory request.

    Returns:
        SearchMemoryResponse: Search results.
    """
    use_case = get_search_use_case()

    session_id = UUID(request.sessionId) if request.sessionId else None

    result = await use_case.execute(
        query=request.query,
        user_id=request.userId,
        time_filter=request.timeFilter,
        tier=request.tier,
        session_id=session_id,
        max_results=request.maxResults,
        temporal_types=request.temporalTypes,
    )

    return SearchMemoryResponse(**result)


# Configure endpoint for router
search_endpoint_config = {
    "path": "/search",
    "response_model": SearchMemoryResponse,
}
