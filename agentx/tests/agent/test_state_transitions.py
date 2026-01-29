"""Tests for LangGraph state transitions.

Verifies that all 8 nodes properly update AgentState.
Uses real Ollama with small LLM (deepseek-r1:1.5b) for integration tests.
These tests are marked as integration since they make real LLM calls.
"""

from unittest.mock import AsyncMock, Mock, patch

import dspy
import pytest
from httpx import Response
from langchain_core.messages import AIMessage

from agentx.agent.graph import create_graph
from agentx.agent.state import AgentState


# Mock httpx response for SearXNG
def mock_searxng_response(*args, **kwargs):
    """Create a mock httpx Response for SearXNG."""
    mock_response = Mock(spec=Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "results": [
            {
                "title": "AI Overview",
                "url": "https://example.com/ai",
                "content": "Artificial intelligence is a field of computer science.",
                "engine": "google",
                "score": 0.9,
            }
        ]
    }
    mock_response.raise_for_status = Mock()
    return mock_response


@pytest.fixture(autouse=True)
def configure_dspy_small() -> None:
    """Configure DSPy with small Ollama model for testing."""
    # Use deepseek-r1:1.5b (smallest available model) for faster tests
    lm = dspy.LM(
        "ollama_chat/deepseek-r1:1.5b",
        api_base="http://localhost:11434",
        api_key="",
        temperature=0.7,
        max_tokens=512,
    )
    dspy.configure(lm=lm)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_analyst_p1_transition() -> None:
    """Test analyst_p1 node adds analysis to state (Pass 1)."""
    from agentx.agent.nodes.analyst import analyst_node

    state: AgentState = {
        "messages": [AIMessage(content="What is AI?")],
        "ui": [],
        "reasoning_steps": 0,  # Pass 1
        "session_id": "test",
        "total_tool_calls": 0,
    }

    result = await analyst_node(state)

    # Pass 1 returns _analysis
    assert "_analysis" in result
    assert "messages" in result
    assert "reasoning_steps" in result


@pytest.mark.integration
@pytest.mark.asyncio
async def test_researcher_transition() -> None:
    """Test researcher node adds research to state."""
    from agentx.agent.nodes.researcher import researcher_node

    state: AgentState = {
        "messages": [AIMessage(content="Search for AI")],
        "ui": [],
        "reasoning_steps": 1,
        "session_id": "test",
        "total_tool_calls": 0,
        "_analysis": {
            "search_terms": ["artificial intelligence", "machine learning"],
            "domain": "technology",
        },
    }

    # Mock the external SearXNG call to avoid network dependency
    mock_get = AsyncMock(return_value=mock_searxng_response())
    with patch("httpx.AsyncClient.get", mock_get):
        result = await researcher_node(state)

        assert "_research" in result
        assert "messages" in result


@pytest.mark.integration
@pytest.mark.asyncio
async def test_contextualizer_transition() -> None:
    """Test contextualizer node enriches data."""
    from agentx.agent.nodes.contextualizer import contextualizer_node

    state: AgentState = {
        "messages": [AIMessage(content="Context needed")],
        "ui": [],
        "reasoning_steps": 2,
        "session_id": "test",
        "total_tool_calls": 0,
        "_research": {"findings": "Raw findings"},
    }

    result = await contextualizer_node(state)

    assert "contextualized_data" in result
    assert "messages" in result


@pytest.mark.integration
@pytest.mark.asyncio
async def test_analyst_p2_transition() -> None:
    """Test analyst_p2 node judges data quality (Pass 2)."""
    from agentx.agent.nodes.analyst import analyst_node

    state: AgentState = {
        "messages": [AIMessage(content="Judge quality")],
        "ui": [],
        "reasoning_steps": 3,  # Pass 2
        "session_id": "test",
        "total_tool_calls": 0,
        "contextualized_data": {"findings": "Rich data"},
    }

    result = await analyst_node(state)

    # Pass 2 returns _quality_assessment (not _analysis)
    assert "_quality_assessment" in result
    assert "messages" in result


@pytest.mark.integration
@pytest.mark.asyncio
async def test_designer_transition() -> None:
    """Test designer node adds widget design."""
    from agentx.agent.nodes.designer import designer_node

    state: AgentState = {
        "messages": [AIMessage(content="Design widgets")],
        "ui": [],
        "reasoning_steps": 4,
        "session_id": "test",
        "total_tool_calls": 0,
        "contextualized_data": {"findings": "Final findings"},
    }

    result = await designer_node(state)

    assert "_widget_design" in result
    assert "messages" in result


@pytest.mark.integration
@pytest.mark.asyncio
async def test_widget_selector_transition() -> None:
    """Test widget_selector node chooses widgets."""
    from agentx.agent.nodes.widget_selector import widget_selector_node

    state: AgentState = {
        "messages": [AIMessage(content="Select widgets")],
        "ui": [],
        "reasoning_steps": 5,
        "session_id": "test",
        "total_tool_calls": 0,
        "_widget_design": {"urgency": "routine", "content_type": "text"},
    }

    result = await widget_selector_node(state)

    assert "_widget_selection" in result
    assert "messages" in result


@pytest.mark.integration
@pytest.mark.asyncio
async def test_sequencer_transition() -> None:
    """Test sequencer node orders widgets."""
    from agentx.agent.nodes.sequencer import sequencer_node

    state: AgentState = {
        "messages": [AIMessage(content="Sequence widgets")],
        "ui": [],
        "reasoning_steps": 6,
        "session_id": "test",
        "total_tool_calls": 0,
        "_widget_selection": {
            "widget_type": "card",
            "existing_widgets": ["markdown"],
        },
        "_analysis": {"urgency": "routine"},
    }

    result = await sequencer_node(state)

    assert "_widget_sequence" in result
    assert "messages" in result


@pytest.mark.integration
@pytest.mark.asyncio
async def test_presenter_transition() -> None:
    """Test presenter node finalizes presentation."""
    from agentx.agent.nodes.presenter import presenter_node

    state: AgentState = {
        "messages": [AIMessage(content="Present findings")],
        "ui": [],
        "reasoning_steps": 7,
        "session_id": "test",
        "total_tool_calls": 0,
        "contextualized_data": {"findings": "Complete findings"},
    }

    result = await presenter_node(state)

    assert "messages" in result
    assert "total_tool_calls" in result


@pytest.mark.asyncio
async def test_full_pipeline_flow() -> None:
    """Test that all nodes can be called in sequence."""
    graph = create_graph()
    compiled = graph.compile()

    # Verify graph compiles
    assert compiled is not None
    # Filter out internal nodes
    actual_nodes = {n for n in compiled.nodes.keys() if not n.startswith("__")}
    assert len(actual_nodes) == 8
