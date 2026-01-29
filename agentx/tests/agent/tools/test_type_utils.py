"""Unit tests for type conversion utilities.

Tests all fallback paths for _to_float and _to_bool functions.
"""

from agentx.agent.tools.common.type_utils import _to_bool, _to_float


class TestToFloat:
    """Tests for _to_float function."""

    def test_none_value_returns_default(self) -> None:
        """Test that None returns the default value."""
        assert _to_float(None) == 0.5
        assert _to_float(None, default=0.8) == 0.8

    def test_bool_values_convert(self) -> None:
        """Test that booleans convert to 1.0 or 0.0."""
        assert _to_float(True) == 1.0
        assert _to_float(False) == 0.0

    def test_numeric_values_pass_through(self) -> None:
        """Test that int and float values pass through."""
        assert _to_float(0) == 0.0
        assert _to_float(1) == 1.0
        assert _to_float(0.75) == 0.75
        assert _to_float(3.14159) == 3.14159

    def test_string_floats_convert(self) -> None:
        """Test that string floats convert correctly."""
        assert _to_float("0.75") == 0.75
        assert _to_float("0.0") == 0.0
        assert _to_float("1.0") == 1.0
        assert _to_float("  0.5  ") == 0.5

    def test_text_scores_map(self) -> None:
        """Test that text-based scores map to values."""
        assert _to_float("very high") == 0.95
        assert _to_float("high") == 0.85
        assert _to_float("good") == 0.75
        assert _to_float("medium") == 0.50
        assert _to_float("moderate") == 0.50
        assert _to_float("low") == 0.25
        assert _to_float("very low") == 0.15
        assert _to_float("poor") == 0.20

    def test_text_scores_case_insensitive(self) -> None:
        """Test that text scores are case-insensitive."""
        assert _to_float("HIGH") == 0.85
        assert _to_float("Medium") == 0.50
        assert _to_float("  Low  ") == 0.25

    def test_percentages_convert(self) -> None:
        """Test that percentage strings convert correctly."""
        assert _to_float("75%") == 0.75
        assert _to_float("100%") == 1.0
        assert _to_float("0%") == 0.0
        assert _to_float("  50%  ") == 0.50

    def test_invalid_returns_default(self) -> None:
        """Test that invalid values return default."""
        assert _to_float("invalid") == 0.5
        assert _to_float("abc") == 0.5
        assert _to_float([], default=0.3) == 0.3

    def test_edge_cases(self) -> None:
        """Test edge cases."""
        # Zero values
        assert _to_float(0) == 0.0
        assert _to_float("0") == 0.0
        assert _to_float("0%") == 0.0

        # Negative values (as floats)
        assert _to_float(-0.5) == -0.5
        assert _to_float("-0.5") == -0.5


class TestToBool:
    """Tests for _to_bool function."""

    def test_none_value_returns_default(self) -> None:
        """Test that None returns the default value."""
        assert _to_bool(None) is False
        assert _to_bool(None, default=True) is True

    def test_bool_values_pass_through(self) -> None:
        """Test that bool values pass through."""
        assert _to_bool(True) is True
        assert _to_bool(False) is False

    def test_numeric_values_convert(self) -> None:
        """Test that numeric values convert to bool."""
        assert _to_bool(1) is True
        assert _to_bool(0) is False
        assert _to_bool(2) is True
        assert _to_bool(-1) is True
        assert _to_bool(1.0) is True
        assert _to_bool(0.0) is False

    def test_true_values_convert(self) -> None:
        """Test that true-ish strings convert to True."""
        true_strings = ["true", "yes", "1", "t", "y", "high", "good", "very high"]
        for s in true_strings:
            assert _to_bool(s) is True, f"Failed for: {s}"

    def test_false_values_convert(self) -> None:
        """Test that false-ish strings convert to False."""
        false_strings = ["false", "no", "0", "f", "n", "low", "poor", "very low"]
        for s in false_strings:
            assert _to_bool(s) is False, f"Failed for: {s}"

    def test_case_insensitive(self) -> None:
        """Test that conversion is case-insensitive."""
        assert _to_bool("TRUE") is True
        assert _to_bool("Yes") is True
        assert _to_bool("  HIGH  ") is True
        assert _to_bool("FALSE") is False
        assert _to_bool("No") is False

    def test_invalid_returns_default(self) -> None:
        """Test that invalid values return default."""
        assert _to_bool("invalid") is False
        assert _to_bool("maybe") is False
        assert _to_bool([], default=True) is True
