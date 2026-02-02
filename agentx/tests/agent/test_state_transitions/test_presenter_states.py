"""Tests for presenter node state transitions."""

import pytest
from langchain_core.messages import AIMessage

from agentx.agent.nodes.presenter import presenter_node
from agentx.agent.state import AgentState


@pytest.mark.integration
@pytest.mark.asyncio
async def test_presenter_transition() -> None:
    """Test presenter node finalizes presentation."""
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
