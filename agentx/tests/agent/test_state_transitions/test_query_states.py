"""Tests for query processing node state transitions.

Tests for analyst_p1, researcher, and contextualizer nodes.
"""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import Response
from langchain_core.messages import AIMessage

from agentx.agent.nodes.analyst import analyst_node
from agentx.agent.nodes.contextualizer import contextualizer_node
from agentx.agent.nodes.researcher import researcher_node
from agentx.agent.state import AgentState


def mock_searxng_response(*args, **kwargs):
    """Create a mock httpx Response for SearXNG."""
    from unittest.mock import Mock

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


@pytest.mark.integration
@pytest.mark.asyncio
async def test_analyst_p1_transition() -> None:
    """Test analyst_p1 node adds analysis to state (Pass 1)."""
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
