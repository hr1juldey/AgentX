# =============================================================================
# AGENTX R014 - Smoke Tests for DSPy Configuration
# =============================================================================

import pytest
import dspy
from config.dspy import configure_dspy, get_lm_info


@pytest.mark.requires_ollama
def test_dspy_configures_successfully():
    """Test DSPy can be configured with Ollama."""
    configure_dspy()
    lm_info = get_lm_info()

    assert lm_info is not None
    assert "provider" in lm_info
    assert lm_info["provider"] == "ollama"
    assert "model" in lm_info


@pytest.mark.requires_ollama
def test_dspy_basic_lm_call():
    """Test basic DSPy LM call works."""
    from config.dspy import configure_dspy

    configure_dspy()

    # Simple test prediction
    predict = dspy.Predict("question -> answer")
    result = predict(question="What is 2+2?")

    assert hasattr(result, "answer")
    assert result.answer is not None
    assert len(str(result.answer)) > 0
