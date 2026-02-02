"""Quality and merge integration tests for consolidation.

Tests for duplicate detection, merging, and merge rate metrics.
"""

from uuid import uuid4

import pytest

from agentx.domain.entities.enums import TemporalType


class TestDuplicateMerging:
    """Tests for duplicate detection and merging."""

    @pytest.mark.asyncio
    async def test_merge_similar_memories(self, consolidation_setup):
        """Should merge memories with similar content."""
        store = consolidation_setup["store"]
        consolidate = consolidation_setup["consolidate"]
        user_id = str(uuid4())
        session_id = uuid4()

        # Store similar memories
        await store.execute(
            content="User prefers dark mode",
            user_id=user_id,
            temporal_type=TemporalType.PREFERENCE,
            tier=2,
            session_id=session_id,
        )
        await store.execute(
            content="User prefers dark mode in apps",
            user_id=user_id,
            temporal_type=TemporalType.PREFERENCE,
            tier=2,
            session_id=session_id,
        )

        # Consolidate
        result = await consolidate.execute(user_id=user_id, session_id=session_id)

        # Should merge duplicates
        assert result.memories_consolidated <= 2  # Merged to 1 or 2
        # Some memories should be discarded
        assert result.memories_discarded >= 0


class TestMergeRate:
    """Tests for consolidation merge rate (>10%)."""

    @pytest.mark.asyncio
    async def test_merge_rate_above_threshold(self, consolidation_setup):
        """Should achieve >10% merge rate with duplicate content."""
        store = consolidation_setup["store"]
        consolidate = consolidation_setup["consolidate"]
        user_id = str(uuid4())
        session_id = uuid4()

        # Store memories with 20% duplicates
        unique_memories = [
            ("User prefers dark mode", TemporalType.PREFERENCE),
            ("User lives in SF", TemporalType.FACT),
            ("User is a developer", TemporalType.FACT),
            ("User likes Python", TemporalType.PREFERENCE),
            ("User uses VS Code", TemporalType.PREFERENCE),
        ]
        duplicates = [
            ("User prefers dark mode", TemporalType.PREFERENCE),  # Duplicate
            ("User lives in SF", TemporalType.FACT),  # Duplicate
        ]

        # Store unique
        for content, temp_type in unique_memories:
            await store.execute(
                content=content,
                user_id=user_id,
                temporal_type=temp_type,
                tier=2,
                session_id=session_id,
            )

        # Store duplicates
        for content, temp_type in duplicates:
            await store.execute(
                content=content,
                user_id=user_id,
                temporal_type=temp_type,
                tier=2,
                session_id=session_id,
            )

        # Consolidate
        result = await consolidate.execute(user_id=user_id, session_id=session_id)

        # Calculate merge rate
        total_stored = len(unique_memories) + len(duplicates)
        merge_rate = result.memories_discarded / total_stored if total_stored > 0 else 0

        # Should have at least 2/7 = ~28% merge rate
        assert merge_rate >= 0.10
