"""Shared fixtures for consolidation integration tests.

From C005 memory-rag change.
"""

import pytest

from agentx.application.use_cases.consolidate_memory_use_case import (
    ConsolidateMemoryUseCase,
)
from agentx.application.use_cases.store_memory_use_case import StoreMemoryUseCase
from agentx.application.services.duration_memory_service import (
    DurationMemoryService,
)
from agentx.application.services.temporal_rag_service import TemporalRAGService
from agentx.infrastructure.database.qdrant_vector_store import QdrantVectorStore


@pytest.fixture
async def consolidation_setup():
    """Setup test environment for consolidation tests."""
    import httpx

    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get("http://localhost:6335/")
        if response.status_code != 200:
            pytest.skip("Qdrant not available")
    except Exception:
        pytest.skip("Qdrant not available")

    vector_store = QdrantVectorStore()
    temporal_service = TemporalRAGService(vector_store=vector_store)
    duration_service = DurationMemoryService(vector_store=vector_store)
    store_use_case = StoreMemoryUseCase(temporal_service=temporal_service)
    consolidate_use_case = ConsolidateMemoryUseCase(
        vector_store=vector_store, duration_svc=duration_service
    )

    return {
        "vector_store": vector_store,
        "store": store_use_case,
        "consolidate": consolidate_use_case,
    }
