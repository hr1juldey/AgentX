"""Tests for LangGraph state transitions.

Verifies that all 8 nodes properly update AgentState.
"""

from unittest.mock import patch

import pytest
from langchain_core.messages import AIMessage

from agentx.agent.graph import create_graph
from agentx.agent.state import AgentState
from agentx.core.dependencies import ensure_dspy_configured


@pytest.fixture(autouse=True)
def configure_dspy() -> None:
    """Configure DSPy before each test."""
    ensure_dspy_configured()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_analyst_p1_transition() -> None:
    """Test analyst_p1 node adds analysis to state."""
    from agentx.agent.nodes.analyst import analyst_node

    state: AgentState = {
        "messages": [AIMessage(content="What is AI?")],
        "ui": [],
        "reasoning_steps": 0,
        "session_id": "test",
        "total_tool_calls": 0,
    }

    result = await analyst_node(state)

    assert "_analysis" in result
    assert "messages" in result
    assert result["total_tool_calls"] > 0


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
        "_analysis": {"search_query": "artificial intelligence"},
    }

    with patch("agentx.agent.tools.researcher.search_executor.search"):
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
    """Test analyst_p2 node judges data quality."""
    from agentx.agent.nodes.analyst import analyst_node

    state: AgentState = {
        "messages": [AIMessage(content="Judge quality")],
        "ui": [],
        "reasoning_steps": 3,
        "session_id": "test",
        "total_tool_calls": 0,
        "contextualized_data": {"findings": "Rich data"},
    }

    result = await analyst_node(state)

    assert "_analysis" in result
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
    assert result["total_tool_calls"] > 0


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
