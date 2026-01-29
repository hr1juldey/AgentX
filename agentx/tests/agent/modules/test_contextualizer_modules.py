"""Unit tests for Contextualizer agent modules with real Ollama LLM.

Tests individual DSPy modules from the contextualizer agent:
- RelevanceScorerModule
- ContextFilterModule
- ContextInjectorModule
"""

from typing import cast

import dspy
import pytest

from agentx.agent.tools.contextualizer.contextualizer import ContextInjectorModule
from agentx.agent.tools.contextualizer.filter import ContextFilterModule
from agentx.agent.tools.contextualizer.reranker import RelevanceScorerModule

# Type alias for DSPy module results (pyrefly workaround)
ModuleResult = dict[str, object]


@pytest.fixture(autouse=True)
def configure_dspy_small() -> None:
    """Configure DSPy with small Ollama model for testing."""
    lm = dspy.LM(
        "ollama_chat/deepseek-r1:1.5b",
        api_base="http://localhost:11434",
        api_key="",
        temperature=0.7,
        max_tokens=512,
    )
    dspy.configure(lm=lm)


@pytest.mark.integration
def test_relevance_scorer_module() -> None:
    """Test RelevanceScorerModule with real LLM."""
    module = RelevanceScorerModule()

    context_chunks = [
        {
            "text": "Artificial intelligence is transforming healthcare.",
            "source": "test",
        },
    ]

    result = cast(
        ModuleResult,
        module(
            query="How is AI used in healthcare?",
            context_chunks=context_chunks,
        ),
    )

    assert "reordered_context" in result
    assert "scores" in result
    print(
        f"RelevanceScorer: reordered={len(result.get('reordered_context', []))} chunks"
    )


@pytest.mark.integration
def test_context_filter_module() -> None:
    """Test ContextFilterModule with real LLM."""
    module = ContextFilterModule()

    context_chunks = [
        {"text": "AI is a field of computer science.", "source": "test1"},
        {"text": "Machine learning is a subset of AI.", "source": "test2"},
        {"text": "Bananas are yellow fruits.", "source": "test3"},  # Irrelevant
    ]

    result = cast(
        ModuleResult,
        module(
            query="What is artificial intelligence?",
            context_chunks=context_chunks,
        ),
    )

    assert "filtered_context" in result
    assert "stats" in result
    filtered_context = result.get("filtered_context", [])
    assert isinstance(filtered_context, list)
    print(f"ContextFilter: {len(filtered_context)} chunks kept")


@pytest.mark.integration
def test_context_injector_module() -> None:
    """Test ContextInjectorModule with real LLM."""
    module = ContextInjectorModule()

    additional_context = [
        {"text": "Recent advances include GPT-4 and Claude.", "source": "ai-news"}
    ]

    result = cast(
        ModuleResult,
        module(
            findings="AI is a growing field.",
            context=additional_context,
            query="Tell me about recent AI advances.",
        ),
    )

    assert "enriched_findings" in result
    assert isinstance(result["enriched_findings"], str)
    print(f"ContextInjector: {result['enriched_findings'][:100]}...")
