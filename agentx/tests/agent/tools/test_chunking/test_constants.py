"""Tests for chunking constants."""

from agentx.agent.tools.common.chunking import ITERATIONS, MAX_CHUNK_SIZE, OVERLAP


class TestConstants:
    """Tests for chunking constants."""

    def test_max_chunk_size(self) -> None:
        """Test MAX_CHUNK_SIZE constant."""
        assert MAX_CHUNK_SIZE == 500

    def test_overlap(self) -> None:
        """Test OVERLAP constant."""
        assert OVERLAP == 100

    def test_iterations(self) -> None:
        """Test ITERATIONS constant."""
        assert ITERATIONS == 3
