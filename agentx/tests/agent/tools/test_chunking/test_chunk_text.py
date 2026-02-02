"""Tests for chunk_text function."""

from agentx.agent.tools.common.chunking import chunk_text


class TestChunkText:
    """Tests for chunk_text function."""

    def test_empty_text_returns_single_empty_chunk(self) -> None:
        """Test that empty text returns a single empty chunk."""
        assert chunk_text("") == [""]

    def test_text_shorter_than_chunk_size_returns_single_chunk(self) -> None:
        """Test that short text returns a single chunk."""
        text = "This is a short text."
        assert chunk_text(text, chunk_size=100) == [text]

    def test_text_exactly_chunk_size_returns_single_chunk(self) -> None:
        """Test that text exactly at chunk size returns a single chunk."""
        text = "a" * 100
        assert chunk_text(text, chunk_size=100) == [text]

    def test_text_longer_than_chunk_size_splits_correctly(self) -> None:
        """Test that long text splits into multiple chunks with overlap."""
        text = "a" * 600
        chunks = chunk_text(text, chunk_size=500, overlap=100)
        assert len(chunks) == 2
        assert len(chunks[0]) == 500
        assert len(chunks[1]) == 200  # Last chunk is shorter
        # Check overlap
        assert chunks[0][400:] == chunks[1][:100]

    def test_overlap_zero_returns_non_overlapping_chunks(self) -> None:
        """Test that zero overlap returns non-overlapping chunks."""
        text = "a" * 1000
        chunks = chunk_text(text, chunk_size=500, overlap=0)
        assert len(chunks) == 2
        assert chunks[0] == "a" * 500
        assert chunks[1] == "a" * 500

    def test_custom_chunk_size(self) -> None:
        """Test chunking with custom chunk size."""
        text = "a" * 100
        chunks = chunk_text(text, chunk_size=30, overlap=10)
        # With 100 chars, chunk_size=30, overlap=10:
        # [0-30], [20-50], [40-70], [60-90], [80-100] = 5 chunks
        assert len(chunks) == 5
        # Verify all characters are accounted for
        combined = "".join(chunks)
        # With overlap, combined will be longer than original
        assert len(combined) >= len(text)
