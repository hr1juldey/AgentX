"""Tests for quality assessment node state transitions.

Tests for analyst_p2 node.
"""

import pytest
from langchain_core.messages import AIMessage

from agentx.agent.nodes.analyst import analyst_node
from agentx.agent.state import AgentState


@pytest.mark.integration
@pytest.mark.asyncio
async def test_analyst_p2_transition() -> None:
    """Test analyst_p2 node judges data quality (Pass 2)."""
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
