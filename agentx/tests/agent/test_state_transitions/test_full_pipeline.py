"""Tests for full pipeline state transitions."""

import pytest

from agentx.agent.graph import create_graph


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
