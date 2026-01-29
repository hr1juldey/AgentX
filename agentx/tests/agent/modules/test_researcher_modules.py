"""Unit tests for Researcher agent modules with real Ollama LLM.

Tests individual DSPy modules from the researcher agent:
- DataStructurerModule
- FindingsBeautifierModule
- CitationBuilderModule
"""

from typing import cast
from unittest.mock import Mock

import dspy
import pytest
from httpx import Response

from agentx.agent.tools.researcher.citation_builder import CitationBuilderModule
from agentx.agent.tools.researcher.data_structurer import DataStructurerModule
from agentx.agent.tools.researcher.findings_beautifier import FindingsBeautifierModule

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


def mock_httpx_response(results: list) -> Mock:
    """Create a mock httpx Response."""
    mock_response = Mock(spec=Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"results": results}
    mock_response.raise_for_status = Mock()
    return mock_response


@pytest.mark.integration
def test_data_structurer_module() -> None:
    """Test DataStructurerModule with real LLM."""
    module = DataStructurerModule()

    raw_data = [
        {
            "title": "AI Overview",
            "url": "https://example.com/ai",
            "snippet": "Artificial intelligence is a field of computer science.",
            "engine": "google",
        },
        {
            "title": "Machine Learning Basics",
            "url": "https://example.com/ml",
            "snippet": "Machine learning is a subset of AI.",
            "engine": "bing",
        },
    ]

    result = cast(
        ModuleResult,
        module(raw_results=str(raw_data), query_context="AI research results"),
    )

    assert "structured_data" in result
    # structured_data is a list
    structured_data = result.get("structured_data")
    assert isinstance(structured_data, list)
    print(f"DataStructurer: {len(structured_data)} sources structured")


@pytest.mark.integration
def test_findings_beautifier_module() -> None:
    """Test FindingsBeautifierModule with real LLM."""
    module = FindingsBeautifierModule()

    structured_data = [
        {
            "source_title": "AI Overview",
            "source_url": "https://example.com/ai",
            "snippet": "AI is a field of CS.",
        },
        {
            "source_title": "ML Guide",
            "source_url": "https://example.com/ml",
            "snippet": "ML is subset of AI.",
        },
    ]
    citations = [
        {"title": "AI Overview", "url": "https://example.com/ai", "relevance": 0.9},
        {"title": "ML Guide", "url": "https://example.com/ml", "relevance": 0.8},
    ]

    result = cast(
        ModuleResult,
        module(
            structured_data=structured_data, citations=citations, query="What is AI?"
        ),
    )

    assert "beautified_findings" in result or "findings" in result
    # Check for either output key name
    findings = result.get("beautified_findings") or result.get("findings", "")
    assert isinstance(findings, str)
    assert len(findings) > 0
    # Beautified findings should be more readable than raw
    print(f"FindingsBeautifier: {findings[:200]}...")


@pytest.mark.integration
def test_citation_builder_module() -> None:
    """Test CitationBuilderModule with real LLM."""
    module = CitationBuilderModule()

    structured_data = [
        {
            "source_title": "AI Overview",
            "source_url": "https://example.com/ai",
            "snippet": "AI is a field of CS.",
            "published_date": "2023",
        },
        {
            "source_title": "ML Guide",
            "source_url": "https://example.com/ml",
            "snippet": "ML is subset of AI.",
            "published_date": "2023",
        },
    ]

    result = cast(
        ModuleResult, module(structured_data=structured_data, query="What is AI?")
    )

    assert "citations" in result
    # citations is a list
    citations = result.get("citations")
    assert isinstance(citations, list)
    assert len(citations) > 0
    print(f"CitationBuilder: {len(citations)} citations built")
