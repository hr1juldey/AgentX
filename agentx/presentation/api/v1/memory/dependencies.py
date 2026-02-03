"""Use case dependencies for memory routes.

Provides dependency injection for memory use cases.
"""

from agentx.application.use_cases.consolidate_memory_use_case import (
    ConsolidateMemoryUseCase,
)
from agentx.application.use_cases.search_memory_use_case import SearchMemoryUseCase
from agentx.application.use_cases.store_memory_use_case import StoreMemoryUseCase
from agentx.application.services.duration_memory_service import (
    DurationMemoryService,
)
from agentx.application.services.temporal_rag_service import TemporalRAGService
from agentx.core.dependencies import get_vector_store


def get_store_use_case() -> StoreMemoryUseCase:
    """Get store memory use case instance.

    Returns:
        StoreMemoryUseCase: Use case instance.
    """
    vector_store = get_vector_store()
    temporal_rag = TemporalRAGService(vector_store=vector_store)
    return StoreMemoryUseCase(vector_store=vector_store, temporal_rag=temporal_rag)


def get_search_use_case() -> SearchMemoryUseCase:
    """Get search memory use case instance.

    Returns:
        SearchMemoryUseCase: Use case instance.
    """
    vector_store = get_vector_store()
    temporal_rag = TemporalRAGService(vector_store=vector_store)
    return SearchMemoryUseCase(vector_store=vector_store, temporal_rag=temporal_rag)


def get_consolidate_use_case() -> ConsolidateMemoryUseCase:
    """Get consolidate memory use case instance.

    Returns:
        ConsolidateMemoryUseCase: Use case instance.
    """
    vector_store = get_vector_store()
    duration_svc = DurationMemoryService()
    return ConsolidateMemoryUseCase(
        vector_store=vector_store, duration_svc=duration_svc
    )


def get_duration_service() -> DurationMemoryService:
    """Get duration memory service instance.

    Returns:
        DurationMemoryService: Service instance.
    """
    return DurationMemoryService()
