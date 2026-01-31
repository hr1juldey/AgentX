"""Unit tests for ConsolidateMemoryUseCase.

Tests Tier 2 to Tier 3 migration, duplicate merging, invalidation.
From C005 memory-rag change.
"""

from datetime import datetime, timedelta
from uuid import uuid4

import pytest

from agentx.application.use_cases.consolidate_memory_use_case import (
    ConsolidateMemoryUseCase,
)
from agentx.domain.entities.enums import TemporalType


class MockVectorStore:
    """Mock QdrantVectorStore for testing."""

    def __init__(self):
        self.tier2_memories = [
            {
                "memory_id": "1",
                "content": "User prefers dark mode in apps",
                "metadata": {
                    "temporal_type": TemporalType.PREFERENCE.value,
                    "created_at": datetime.now().isoformat(),
                },
            },
            {
                "memory_id": "2",
                "content": "User prefers dark mode",
                "metadata": {
                    "temporal_type": TemporalType.PREFERENCE.value,
                    "created_at": datetime.now().isoformat(),
                },
            },
            {
                "memory_id": "3",
                "content": "User lives in New York",
                "metadata": {
                    "temporal_type": TemporalType.FACT.value,
                    "created_at": datetime.now().isoformat(),
                    "superseded_by": "4",
                },
            },
        ]
        self.tier3_count = 0

    async def get_all_memories(self, user_id, tier=2, session_id=None):
        """Return mock Tier 2 memories."""
        return self.tier2_memories

    async def store_memory(
        self,
        content,
        user_id,
        memory_type,
        temporal_type,
        tier=3,
        session_id=None,
        metadata=None,
    ):
        """Store to Tier 3."""
        self.tier3_count += 1
        return uuid4()


class MockDurationService:
    """Mock DurationMemoryService."""

    async def consolidate_session_durations(self, user_id, session_id):
        """Return mock consolidation result."""
        from agentx.domain.entities.memory_consolidation import (
            MemoryConsolidationEntity,
        )

        return MemoryConsolidationEntity(
            session_id=session_id,
            user_id=user_id,
            consolidated_at=datetime.now(),
            memories_consolidated=0,
            memories_discarded=0,
            consolidation_summary="No duration events",
        )


@pytest.fixture
def consolidate_use_case():
    """Create ConsolidateMemoryUseCase with mocks."""
    mock_store = MockVectorStore()
    mock_duration = MockDurationService()
    return ConsolidateMemoryUseCase(vector_store=mock_store, duration_svc=mock_duration)


class TestDuplicateMerging:
    """Tests for duplicate memory merging."""

    @pytest.mark.asyncio
    async def test_merge_duplicate_content(self, consolidate_use_case):
        """Should merge memories with similar content."""
        memories = [
            {"content": "User prefers dark mode", "metadata": {}},
            {"content": "User prefers dark mode", "metadata": {}},
            {"content": "Different content", "metadata": {}},
        ]
        merged, discarded = consolidate_use_case._merge_duplicates(memories)
        assert len(merged) == 2  # One dark mode, one different
        assert discarded == 1

    @pytest.mark.asyncio
    async def test_keep_newest_duplicate(self, consolidate_use_case):
        """Should keep the newest version of duplicate memories."""
        now = datetime.now()
        memories = [
            {
                "content": "User prefers dark mode",
                "metadata": {"created_at": (now - timedelta(hours=2)).isoformat()},
            },
            {
                "content": "User prefers dark mode",
                "metadata": {"created_at": now.isoformat()},
            },
        ]
        merged, discarded = consolidate_use_case._merge_duplicates(memories)
        assert len(merged) == 1
        # Should keep the newest (second one)
        assert merged[0]["metadata"]["created_at"] == now.isoformat()


class TestFactInvalidation:
    """Tests for fact invalidation during consolidation."""

    @pytest.mark.asyncio
    async def test_mark_superseded_facts(self, consolidate_use_case):
        """Should mark superseded facts."""
        memories = [
            {
                "content": "Old fact",
                "metadata": {"superseded_by": "123"},
            },
        ]
        result = consolidate_use_case._invalidate_outdated_facts(memories)
        assert result[0].get("superseded") is True

    @pytest.mark.asyncio
    async def test_keep_non_superseded_facts(self, consolidate_use_case):
        """Should not mark non-superseded facts."""
        memories = [
            {
                "content": "Current fact",
                "metadata": {},
            },
        ]
        result = consolidate_use_case._invalidate_outdated_facts(memories)
        assert result[0].get("superseded") is False


class TestConsolidation:
    """Tests for consolidation execution."""

    @pytest.mark.asyncio
    async def test_consolidate_to_tier3(self, consolidate_use_case):
        """Should consolidate memories to Tier 3."""
        from uuid import uuid4

        session_id = uuid4()
        result = await consolidate_use_case.execute(
            user_id="user1", session_id=session_id
        )
        assert result.memories_consolidated > 0

    @pytest.mark.asyncio
    async def test_insufficient_memories(self, consolidate_use_case):
        """Should not consolidate if below minimum threshold."""
        from uuid import uuid4

        # Use mock store with fewer memories
        consolidate_use_case._vector_store.tier2_memories = [
            {"content": "Single memory", "metadata": {}}
        ]
        session_id = uuid4()
        result = await consolidate_use_case.execute(
            user_id="user1", session_id=session_id, min_memories=5
        )
        assert result.memories_consolidated == 0
        assert "Insufficient" in result.consolidation_summary


class TestMergeRate:
    """Tests for consolidation merge rate."""

    @pytest.mark.asyncio
    async def test_merge_rate_calculation(self, consolidate_use_case):
        """Should achieve >10% merge rate with duplicates."""
        # Create mock data with 20% duplicates
        memories = [{"content": f"Memory {i}", "metadata": {}} for i in range(10)]
        # Add 2 duplicates
        memories.append({"content": "Memory 1", "metadata": {}})
        memories.append({"content": "Memory 2", "metadata": {}})

        merged, discarded = consolidate_use_case._merge_duplicates(memories)
        merge_rate = discarded / len(memories)
        assert merge_rate >= 0.15  # 2/12 = ~16.7%
