"""Unit tests for chunking infrastructure.

Tests edge cases (empty, single chunk, multi-chunk).
"""

from agentx.agent.tools.common.chunking import (
    MAX_CHUNK_SIZE,
    OVERLAP,
    ITERATIONS,
    chunk_text,
    chunk_list,
    deduplicate_items,
    iterative_refine,
)


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


class TestDeduplicateItems:
    """Tests for deduplicate_items function."""

    def test_empty_list_returns_empty_list(self) -> None:
        """Test that empty list returns empty list."""
        assert deduplicate_items([]) == []

    def test_unique_items_unchanged(self) -> None:
        """Test that unique items remain unchanged."""
        # Use items longer than default min_length=10
        items = ["apple pie cake", "banana split", "cherry tart"]
        assert deduplicate_items(items) == items

    def test_duplicate_items_removed(self) -> None:
        """Test that duplicate items are removed."""
        # Use items longer than default min_length=10
        items = [
            "apple pie cake",
            "banana split",
            "apple pie cake",
            "cherry tart",
            "banana split",
        ]
        result = deduplicate_items(items)
        assert result == ["apple pie cake", "banana split", "cherry tart"]

    def test_normalization_works(self) -> None:
        """Test that normalization (lowercase, strip) works."""
        # Use items longer than default min_length=10
        items = ["Apple Pie Cake", "  apple pie cake", "APPLE PIE CAKE", "banana split"]
        result = deduplicate_items(items, normalize=True)
        assert result == ["Apple Pie Cake", "banana split"]

    def test_no_normalization_preserves_case(self) -> None:
        """Test that disabling normalization preserves case."""
        # Use items longer than default min_length=10
        items = ["Apple Pie Cake", "apple pie cake", "APPLE PIE CAKE"]
        result = deduplicate_items(items, normalize=False)
        assert result == ["Apple Pie Cake", "apple pie cake", "APPLE PIE CAKE"]

    def test_short_items_filtered(self) -> None:
        """Test that items shorter than min_length are filtered."""
        items = ["long item here", "short", "another long item"]
        result = deduplicate_items(items, min_length=10)
        assert result == ["long item here", "another long item"]

    def test_empty_strings_removed(self) -> None:
        """Test that empty strings are removed."""
        # Use items longer than default min_length=10
        items = ["apple pie cake", "", "banana split", "", "cherry tart"]
        result = deduplicate_items(items)
        assert result == ["apple pie cake", "banana split", "cherry tart"]

    def test_min_length_zero_disables_filter(self) -> None:
        """Test that min_length=0 disables the length filter."""
        items = ["apple", "banana", "cherry"]
        result = deduplicate_items(items, min_length=0)
        assert result == ["apple", "banana", "cherry"]


class TestIterativeRefine:
    """Tests for iterative_refine function."""

    def test_zero_iterations_returns_original(self) -> None:
        """Test that zero iterations returns original items."""
        items = [1, 2, 3]

        def processor(current: list[int], previous: list[int]) -> list[int]:
            return [x + 1 for x in current]

        result = iterative_refine(items, processor, iterations=0)
        assert result == items

    def test_processor_called_correct_times(self) -> None:
        """Test that processor is called the correct number of times."""
        items = [1]
        call_count = [0]

        def processor(current: list[int], previous: list[int]) -> list[int]:
            call_count[0] += 1
            return [x + 1 for x in current]

        result = iterative_refine(items, processor, iterations=3)
        assert call_count[0] == 3
        assert result == [4]  # 1 + 1 + 1 + 1

    def test_previous_parameter_populated(self) -> None:
        """Test that previous parameter is populated correctly."""
        items = [1]

        def processor(current: list[int], previous: list[int]) -> list[int]:
            if not previous:
                return [10]
            else:
                # Should see the previous iteration's result
                return previous + [20]

        result = iterative_refine(items, processor, iterations=3)
        # Iteration 1: previous=[], returns [10]
        # Iteration 2: previous=[10], returns [10, 20]
        # Iteration 3: previous=[10, 20], returns [10, 20, 20]
        assert result == [10, 20, 20]

    def test_default_iterations(self) -> None:
        """Test that default ITERATIONS constant is used."""
        items = [1]
        call_count = [0]

        def processor(current: list[int], previous: list[int]) -> list[int]:
            call_count[0] += 1
            return current

        iterative_refine(items, processor)
        assert call_count[0] == ITERATIONS


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
