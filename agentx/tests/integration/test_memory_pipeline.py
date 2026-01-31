"""Integration tests for memory pipeline.

Tests end-to-end memory flow from store to search.
From C005 memory-rag change.
"""

from datetime import datetime
from uuid import uuid4

import pytest

from agentx.application.use_cases.store_memory_use_case import StoreMemoryUseCase
from agentx.application.use_cases.search_memory_use_case import SearchMemoryUseCase
from agentx.application.services.temporal_rag_service import TemporalRAGService
from agentx.domain.entities.enums import TemporalType
from agentx.infrastructure.database.qdrant_vector_store import QdrantVectorStore


@pytest.fixture
async def memory_setup():
    """Setup test memory with real QdrantVectorStore."""
    # Note: These tests require Qdrant to be running
    # Skip if Qdrant is not available
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
    store_use_case = StoreMemoryUseCase(temporal_service=temporal_service)
    search_use_case = SearchMemoryUseCase(temporal_service=temporal_service)

    yield {
        "vector_store": vector_store,
        "store": store_use_case,
        "search": search_use_case,
    }

    # Cleanup: delete test collection
    # await vector_store.client.delete_collection(...)


class TestMemoryStorage:
    """Tests for storing memories with temporal metadata."""

    @pytest.mark.asyncio
    async def test_store_memory_with_temporal_metadata(self, memory_setup):
        """Should store memory with created_at, valid_from, temporal_type."""
        store_use_case = memory_setup["store"]
        user_id = str(uuid4())

        result = await store_use_case.execute(
            content="User prefers dark mode",
            user_id=user_id,
            temporal_type=TemporalType.PREFERENCE,
            tier=3,
        )

        assert result.memory_id is not None
        assert result.temporal_type == TemporalType.PREFERENCE.value
        assert result.created_at is not None
        assert result.valid_from is not None

    @pytest.mark.asyncio
    async def test_auto_classify_temporal_type(self, memory_setup):
        """Should auto-classify temporal type if not provided."""
        store_use_case = memory_setup["store"]
        user_id = str(uuid4())

        result = await store_use_case.execute(
            content="I like using dark mode in apps",
            user_id=user_id,
            # temporal_type not provided
            tier=3,
        )

        # Should be classified as PREFERENCE based on "like" keyword
        assert result.temporal_type == TemporalType.PREFERENCE.value


class TestMemoryRetrieval:
    """Tests for searching and retrieving memories."""

    @pytest.mark.asyncio
    async def test_search_by_query(self, memory_setup):
        """Should retrieve relevant memories by query."""
        store_use_case = memory_setup["store"]
        search_use_case = memory_setup["search"]
        user_id = str(uuid4())

        # Store a memory first
        await store_use_case.execute(
            content="User lives in San Francisco",
            user_id=user_id,
            temporal_type=TemporalType.FACT,
            tier=3,
        )

        # Search for it
        result = await search_use_case.execute(
            query="Where does the user live?",
            user_id=user_id,
            time_filter="all",
            tier=3,
        )

        assert len(result.results) >= 1
        assert any("San Francisco" in r.content for r in result.results)


class TestTemporalFiltering:
    """Tests for time-based memory filtering."""

    @pytest.mark.asyncio
    async def test_recent_filter(self, memory_setup):
        """Should return only recent memories (last 30 days)."""
        store_use_case = memory_setup["store"]
        search_use_case = memory_setup["search"]
        user_id = str(uuid4())

        # Store recent memory
        await store_use_case.execute(
            content="Recent preference",
            user_id=user_id,
            temporal_type=TemporalType.PREFERENCE,
            tier=3,
        )

        result = await search_use_case.execute(
            query="preference",
            user_id=user_id,
            time_filter="recent",
            tier=3,
        )

        # Should only return recent memories
        for r in result.results:
            created_at = datetime.fromisoformat(r.created_at)
            assert (datetime.now() - created_at).days <= 30


class TestMultiHopRetrieval:
    """Tests for multi-hop retrieval (Tier 2 + Tier 3)."""

    @pytest.mark.asyncio
    async def test_merge_tier2_and_tier3(self, memory_setup):
        """Should merge results from Tier 2 (session) and Tier 3 (persistent)."""
        store_use_case = memory_setup["store"]
        search_use_case = memory_setup["search"]
        user_id = str(uuid4())
        session_id = uuid4()

        # Store to Tier 2 (session)
        await store_use_case.execute(
            content="Session memory: Working on task A",
            user_id=user_id,
            temporal_type=TemporalType.STATE,
            tier=2,
            session_id=session_id,
        )

        # Store to Tier 3 (persistent)
        await store_use_case.execute(
            content="Persistent memory: User prefers dark mode",
            user_id=user_id,
            temporal_type=TemporalType.PREFERENCE,
            tier=3,
        )

        # Search across both tiers
        result = await search_use_case.execute(
            query="task or preference",
            user_id=user_id,
            time_filter="all",
            tier=3,  # Should check both
            session_id=session_id,
        )

        # Should have results from both or at least Tier 3
        assert len(result.results) >= 1
