# =============================================================================
# AGENTX R014 - Smoke Tests for Data Type Handling (Critical Failure Points)
# =============================================================================

import pytest
from services.tools.analyst_tools import (
    DataQualityCheckerModule,
    _to_float,
    _to_bool,
)
from services.tools.contextualizer_tools import (
    RerankerModule,
)
from services.tools.designer_tools import (
    ColorPickerModule,
)


@pytest.mark.requires_ollama
def test_analyst_tools_returns_numeric_completeness():
    """Test DataQualityCheckerModule returns numeric scores."""
    module = DataQualityCheckerModule()

    result = module.forward(
        query="Test query about finance",
        data={"results": [{"title": "Test", "content": "Data"}]},
    )

    # Critical: Must return numeric, not string
    assert "data_completeness" in result
    assert isinstance(result["data_completeness"], (int, float))
    assert 0.0 <= result["data_completeness"] <= 1.0

    # Verify it's NOT a string like "High"
    assert not isinstance(result["data_completeness"], str)


@pytest.mark.requires_ollama
def test_contextualizer_tools_returns_numeric_relevance():
    """Test RerankerModule returns numeric scores."""
    module = RerankerModule()

    results = [
        {"title": "Finance data", "content": "Stock prices..."},
        {"title": "Cooking recipe", "content": "How to bake cake..."},
    ]

    result = module.forward(query="Stock market trends", results=results)

    # Critical: Scores must be numeric
    assert "scores" in result
    assert isinstance(result["scores"], list)

    for score in result["scores"]:
        assert isinstance(score, (int, float))
        assert 0.0 <= score <= 1.0


@pytest.mark.requires_ollama
def test_designer_tools_returns_dict_color_scheme():
    """Test ColorPickerModule returns dict, not string."""
    module = ColorPickerModule()

    result = module.forward(query="Finance dashboard", domain="finance")

    # Critical: color_scheme must be dict
    assert "color_scheme" in result
    assert isinstance(result["color_scheme"], dict)


def test_to_float_helper_handles_text_values():
    """Test _to_float helper converts text to numbers."""
    # Test text mappings
    assert _to_float("High") == 0.85
    assert _to_float("Medium") == 0.50
    assert _to_float("Low") == 0.25
    assert _to_float("Very High") == 0.95

    # Test percentage
    assert _to_float("75%") == 0.75

    # Test numeric
    assert _to_float(0.5) == 0.5
    assert _to_float("0.75") == 0.75

    # Test boolean
    assert _to_float(True) == 1.0
    assert _to_float(False) == 0.0

    # Test default
    assert _to_float(None, default=0.5) == 0.5
    assert _to_float("unknown", default=0.3) == 0.3


def test_to_bool_helper_handles_text_values():
    """Test _to_bool helper converts text to bool."""
    # True values
    assert _to_bool("true") is True
    assert _to_bool("yes") is True
    assert _to_bool("1") is True
    assert _to_bool("high") is True

    # False values
    assert _to_bool("false") is False
    assert _to_bool("no") is False
    assert _to_bool("0") is False
    assert _to_bool("low") is False

    # Boolean
    assert _to_bool(True) is True
    assert _to_bool(False) is False

    # Default
    assert _to_bool(None, default=True) is True
