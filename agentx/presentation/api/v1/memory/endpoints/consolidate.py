"""Consolidate endpoint for memory routes.

POST /consolidate - Consolidate Tier 2 memories to Tier 3.
"""

from agentx.application.dtos.memory_dtos import (
    ConsolidateMemoryRequest,
    ConsolidateMemoryResponse,
)
from agentx.presentation.api.v1.memory.dependencies import get_consolidate_use_case


async def consolidate_memory(
    request: ConsolidateMemoryRequest,
) -> ConsolidateMemoryResponse:
    """Consolidate Tier 2 memories to Tier 3.

    Args:
        request: Consolidate memory request.

    Returns:
        ConsolidateMemoryResponse: Consolidation result.
    """
    from uuid import UUID

    use_case = get_consolidate_use_case()

    result = await use_case.execute(
        user_id=request.userId,
        session_id=UUID(request.sessionId),
        min_memories=request.minMemories,
    )

    return ConsolidateMemoryResponse(  # type: ignore[call-arg]
        sessionId=str(result.session_id),
        userId=result.user_id,
        consolidatedAt=result.consolidated_at.isoformat()
        if result.consolidated_at
        else None,
        memoriesConsolidated=result.memories_consolidated,
        memoriesDiscarded=result.memories_discarded,
        consolidationSummary=result.consolidation_summary,
    )


# Configure endpoint for router
consolidate_endpoint_config = {
    "path": "/consolidate",
    "response_model": ConsolidateMemoryResponse,
}
