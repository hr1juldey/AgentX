"""Tests for design and widget node state transitions.

Tests for designer, widget_selector, and sequencer nodes.
"""

import pytest
from langchain_core.messages import AIMessage

from agentx.agent.nodes.designer import designer_node
from agentx.agent.nodes.sequencer import sequencer_node
from agentx.agent.nodes.widget_selector import widget_selector_node
from agentx.agent.state import AgentState


@pytest.mark.integration
@pytest.mark.asyncio
async def test_designer_transition() -> None:
    """Test designer node adds widget design."""
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
