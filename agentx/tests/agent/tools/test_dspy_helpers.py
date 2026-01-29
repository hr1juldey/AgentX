"""Unit tests for DSPy extraction helpers.

Tests with DSPy Prediction objects.
"""

from agentx.agent.tools.common.dspy_helpers import (
    safe_extract,
    safe_extract_list,
    safe_extract_dict,
)


class MockPrediction:
    """Mock DSPy Prediction object for testing."""

    def __init__(self, **kwargs):
        """Initialize with keyword arguments as attributes."""
        self._data = kwargs

    def __getattr__(self, name: str):
        """Get attribute from internal data."""
        if name in self._data:
            return self._data[name]
        raise AttributeError(
            f"'{type(self).__name__}' object has no attribute '{name}'"
        )

    def get(self, key: str, default=None):
        """Dict-like get method."""
        return self._data.get(key, default)


class TestSafeExtract:
    """Tests for safe_extract function."""

    def test_none_object_returns_default(self) -> None:
        """Test that None object returns default value."""
        assert safe_extract(None, "field", "default") == "default"

    def test_dict_object_returns_value(self) -> None:
        """Test that dict object returns value."""
        data = {"key": "value"}
        assert safe_extract(data, "key", "default") == "value"

    def test_dict_missing_key_returns_default(self) -> None:
        """Test that dict with missing key returns default."""
        data = {"other_key": "value"}
        assert safe_extract(data, "key", "default") == "default"

    def test_dspy_prediction_returns_value(self) -> None:
        """Test that DSPy Prediction object returns value."""
        prediction = MockPrediction(field1="value1")
        assert safe_extract(prediction, "field1", "default") == "value1"

    def test_dspy_prediction_missing_field_returns_default(self) -> None:
        """Test that DSPy Prediction with missing field returns default."""
        prediction = MockPrediction(field1="value1")
        assert safe_extract(prediction, "missing_field", "default") == "default"

    def test_regular_object_returns_attribute(self) -> None:
        """Test that regular object returns attribute value."""

        class RegularObject:
            def __init__(self):
                self.attr = "value"

        obj = RegularObject()
        assert safe_extract(obj, "attr", "default") == "value"

    def test_regular_object_missing_attribute_returns_default(self) -> None:
        """Test that regular object with missing attribute returns default."""

        class RegularObject:
            def __init__(self):
                self.attr = "value"

        obj = RegularObject()
        assert safe_extract(obj, "missing", "default") == "default"

    def test_default_none_is_used(self) -> None:
        """Test that default None is used when no default specified."""
        data = {"key": "value"}
        assert safe_extract(data, "missing") is None


class TestSafeExtractList:
    """Tests for safe_extract_list function."""

    def test_dict_list_returns_list(self) -> None:
        """Test that dict with list returns list."""
        data = {"items": [1, 2, 3]}
        assert safe_extract_list(data, "items") == [1, 2, 3]

    def test_dict_missing_key_returns_empty_list(self) -> None:
        """Test that dict with missing key returns empty list."""
        data = {"other_key": [1, 2, 3]}
        assert safe_extract_list(data, "items") == []

    def test_dict_non_list_value_returns_empty_list(self) -> None:
        """Test that dict with non-list value returns empty list."""
        data = {"items": "not a list"}
        assert safe_extract_list(data, "items") == []

    def test_dspy_prediction_list_returns_list(self) -> None:
        """Test that DSPy Prediction with list returns list."""
        prediction = MockPrediction(items=[1, 2, 3])
        assert safe_extract_list(prediction, "items") == [1, 2, 3]

    def test_dspy_prediction_missing_field_returns_empty_list(self) -> None:
        """Test that DSPy Prediction with missing field returns empty list."""
        prediction = MockPrediction(other_field=[1, 2, 3])
        assert safe_extract_list(prediction, "items") == []


class TestSafeExtractDict:
    """Tests for safe_extract_dict function."""

    def test_dict_dict_returns_dict(self) -> None:
        """Test that dict with dict returns dict."""
        data = {"config": {"key": "value"}}
        assert safe_extract_dict(data, "config") == {"key": "value"}

    def test_dict_missing_key_returns_empty_dict(self) -> None:
        """Test that dict with missing key returns empty dict."""
        data = {"other_key": {"key": "value"}}
        assert safe_extract_dict(data, "config") == {}

    def test_dict_non_dict_value_returns_empty_dict(self) -> None:
        """Test that dict with non-dict value returns empty dict."""
        data = {"config": "not a dict"}
        assert safe_extract_dict(data, "config") == {}

    def test_dspy_prediction_dict_returns_dict(self) -> None:
        """Test that DSPy Prediction with dict returns dict."""
        prediction = MockPrediction(config={"key": "value"})
        assert safe_extract_dict(prediction, "config") == {"key": "value"}

    def test_dspy_prediction_missing_field_returns_empty_dict(self) -> None:
        """Test that DSPy Prediction with missing field returns empty dict."""
        prediction = MockPrediction(other_field={"key": "value"})
        assert safe_extract_dict(prediction, "config") == {}
