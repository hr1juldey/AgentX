"""Memory REST API routes.

Endpoints for memory storage, search, and consolidation.
From C005 memory-rag change.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, status

from agentx.application.dtos.memory_dtos import (
    ConsolidateMemoryRequest,
    ConsolidateMemoryResponse,
    HealthResponse,
    SearchMemoryRequest,
    SearchMemoryResponse,
    StoreMemoryRequest,
    StoreMemoryResponse,
)
from agentx.application.use_cases.consolidate_memory_use_case import (
    ConsolidateMemoryUseCase,
)
from agentx.application.use_cases.search_memory_use_case import SearchMemoryUseCase
from agentx.application.use_cases.store_memory_use_case import StoreMemoryUseCase
from agentx.core.config import get_settings

router = APIRouter()
settings = get_settings()


# Dependency injection (simplified for now)
# TODO: Move to proper DI in core/dependencies.py


def get_store_use_case() -> StoreMemoryUseCase:
    """Get store memory use case instance.

    Returns:
        StoreMemoryUseCase: Use case instance.
    """
    from agentx.infrastructure.database.qdrant_vector_store import QdrantVectorStore
    from agentx.application.services.temporal_rag_service import TemporalRAGService

    vector_store = QdrantVectorStore()
    temporal_rag = TemporalRAGService(vector_store=vector_store)
    return StoreMemoryUseCase(vector_store=vector_store, temporal_rag=temporal_rag)


def get_search_use_case() -> SearchMemoryUseCase:
    """Get search memory use case instance.

    Returns:
        SearchMemoryUseCase: Use case instance.
    """
    from agentx.infrastructure.database.qdrant_vector_store import QdrantVectorStore
    from agentx.application.services.temporal_rag_service import TemporalRAGService

    vector_store = QdrantVectorStore()
    temporal_rag = TemporalRAGService(vector_store=vector_store)
    return SearchMemoryUseCase(vector_store=vector_store, temporal_rag=temporal_rag)


def get_consolidate_use_case() -> ConsolidateMemoryUseCase:
    """Get consolidate memory use case instance.

    Returns:
        ConsolidateMemoryUseCase: Use case instance.
    """
    from agentx.infrastructure.database.qdrant_vector_store import QdrantVectorStore
    from agentx.application.services.duration_memory_service import (
        DurationMemoryService,
    )

    vector_store = QdrantVectorStore()
    duration_svc = DurationMemoryService()
    return ConsolidateMemoryUseCase(
        vector_store=vector_store, duration_svc=duration_svc
    )


# Endpoints


@router.post(
    "/store", response_model=StoreMemoryResponse, status_code=status.HTTP_201_CREATED
)
async def store_memory(request: StoreMemoryRequest) -> StoreMemoryResponse:
    """Store a memory with temporal metadata.

    Args:
        request: Store memory request.

    Returns:
        StoreMemoryResponse: Stored memory details.
    """
    from uuid import UUID

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


@router.post("/search", response_model=SearchMemoryResponse)
async def search_memory(request: SearchMemoryRequest) -> SearchMemoryResponse:
    """Search memories with temporal filtering.

    Args:
        request: Search memory request.

    Returns:
        SearchMemoryResponse: Search results.
    """
    from uuid import UUID

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


@router.post("/consolidate", response_model=ConsolidateMemoryResponse)
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

    return ConsolidateMemoryResponse(
        sessionId=str(result.session_id),
        userId=result.user_id,
        consolidatedAt=result.consolidated_at.isoformat()
        if result.consolidated_at
        else None,
        memoriesConsolidated=result.memories_consolidated,
        memoriesDiscarded=result.memories_discarded,
        consolidationSummary=result.consolidation_summary,
    )


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check for memory services.

    Returns:
        HealthResponse: Health status.
    """
    from datetime import datetime

    # Check Qdrant connection
    qdrant_connected = True
    try:
        from agentx.infrastructure.database.qdrant_vector_store import QdrantVectorStore

        store = QdrantVectorStore()
        store.client.get_collections()
    except Exception:
        qdrant_connected = False

    return HealthResponse(
        status="healthy" if qdrant_connected else "unhealthy",
        qdrant_connected=qdrant_connected,
        timestamp=datetime.now().isoformat(),
    )


# Active states endpoint (for duration tracking)


@router.get("/active-states/{user_id}")
async def get_active_states(user_id: str) -> dict[str, Any]:
    """Get active duration states for a user.

    Args:
        user_id: User identifier.

    Returns:
        dict: Active states summary.
    """
    from agentx.application.services.duration_memory_service import (
        DurationMemoryService,
    )

    svc = DurationMemoryService()
    summary = svc.get_duration_summary()

    return {
        "user_id": user_id,
        "active_states": summary["active_states"],
        "tracked_entities": summary["tracked_entities"],
        "timestamp": summary["timestamp"],
    }
