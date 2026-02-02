"""Tests for chunk_list function."""

from agentx.agent.tools.common.chunking import chunk_list


class TestChunkList:
    """Tests for chunk_list function."""

    def test_empty_list_returns_empty_list(self) -> None:
        """Test that empty list returns empty list of chunks."""
        assert chunk_list([], 5) == []

    def test_list_smaller_than_chunk_size_returns_single_chunk(self) -> None:
        """Test that list smaller than chunk size returns single chunk."""
        items = [1, 2, 3]
        assert chunk_list(items, 5) == [[1, 2, 3]]

    def test_list_exactly_chunk_size_returns_single_chunk(self) -> None:
        """Test that list exactly at chunk size returns single chunk."""
        items = [1, 2, 3, 4, 5]
        assert chunk_list(items, 5) == [[1, 2, 3, 4, 5]]

    def test_list_larger_than_chunk_size_splits_correctly(self) -> None:
        """Test that large list splits into multiple chunks."""
        items = list(range(12))
        chunks = chunk_list(items, 5)
        assert len(chunks) == 3
        assert chunks[0] == [0, 1, 2, 3, 4]
        assert chunks[1] == [5, 6, 7, 8, 9]
        assert chunks[2] == [10, 11]
