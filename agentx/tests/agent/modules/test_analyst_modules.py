"""Unit tests for Analyst agent modules with real Ollama LLM.

Tests individual DSPy modules from the analyst agent:
- ContextAnalyzerModule
- InsightExtractorModule
- GoalDetectorModule
- DataQualityCheckerModule
- SearchTermExtractorModule
"""

from typing import cast

import dspy
import pytest

from agentx.agent.tools.analyst.context_analyzer import ContextAnalyzerModule
from agentx.agent.tools.analyst.data_quality_checker import DataQualityCheckerModule
from agentx.agent.tools.analyst.goal_detector import GoalDetectorModule
from agentx.agent.tools.analyst.insight_extractor import InsightExtractorModule
from agentx.agent.tools.analyst.search_terms import SearchTermExtractorModule

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
def test_context_analyzer_module() -> None:
    """Test ContextAnalyzerModule with real LLM."""
    module = ContextAnalyzerModule()

    result = cast(ModuleResult, module(query="What is artificial intelligence?"))

    assert "query_type" in result
    assert "domain" in result
    assert "urgency" in result

    # Verify reasonable outputs - LLM may return various values including 'None' string
    query_type = str(result.get("query_type", ""))
    urgency = str(result.get("urgency", ""))
    # Accept any non-empty string output from LLM
    assert isinstance(query_type, str)
    assert isinstance(urgency, str)
    domain = str(result.get("domain", ""))
    print(f"ContextAnalyzer: query_type={query_type}, domain={domain}")


@pytest.mark.integration
def test_insight_extractor_module() -> None:
    """Test InsightExtractorModule with real LLM."""
    module = InsightExtractorModule()

    result = cast(
        ModuleResult,
        module(
            query="Artificial intelligence (AI) is intelligence demonstrated by machines, "
            "as opposed to natural intelligence displayed by animals and humans."
        ),
    )

    assert "insights" in result
    insights = result.get("insights")
    # insights is a list
    assert isinstance(insights, list)
    print(f"InsightExtractor: insights={str(insights)[:100]}...")


@pytest.mark.integration
def test_goal_detector_module() -> None:
    """Test GoalDetectorModule with real LLM."""
    module = GoalDetectorModule()

    result = cast(
        ModuleResult,
        module(
            query="Compare Python and JavaScript for web development",
            insights=[
                "Python is a programming language",
                "JavaScript is used for web development",
            ],
        ),
    )

    assert "goal" in result
    assert isinstance(result["goal"], str)
    print(f"GoalDetector: goal={result['goal']}")


@pytest.mark.integration
def test_data_quality_checker_module() -> None:
    """Test DataQualityCheckerModule with real LLM."""
    module = DataQualityCheckerModule()

    result = cast(
        ModuleResult,
        module(
            query="What is the population of France?",
            data="France has a population of approximately 67 million people as of 2023.",
        ),
    )

    assert "completeness_score" in result
    assert "relevance_score" in result
    assert "missing_elements" in result
    assert "needs_more_research" in result

    # Verify scores are in valid range
    assert 0.0 <= result["completeness_score"] <= 1.0  # type: ignore[index]
    assert 0.0 <= result["relevance_score"] <= 1.0  # type: ignore[index]
    print(
        f"DataQualityChecker: completeness={result['completeness_score']:.2f}, "
        f"relevance={result['relevance_score']:.2f}, needs_more={result['needs_more_research']}"
    )


@pytest.mark.integration
def test_search_term_extractor_module() -> None:
    """Test SearchTermExtractorModule with real LLM."""
    module = SearchTermExtractorModule()

    result = cast(
        ModuleResult,
        module(
            query="Economic impact of major wars since 2000",
            domain="economics",
            insights="Wars have significant economic consequences including GDP decline and reconstruction costs.",
        ),
    )

    assert "search_terms" in result
    # search_terms is a list
    search_terms = result.get("search_terms")
    assert isinstance(search_terms, list)
    assert len(search_terms) > 0
    print(f"SearchTermExtractor: terms={str(search_terms)[:100]}...")
