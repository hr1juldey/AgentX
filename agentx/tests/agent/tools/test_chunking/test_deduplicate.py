"""Tests for deduplicate_items function."""

from agentx.agent.tools.common.chunking import deduplicate_items


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
