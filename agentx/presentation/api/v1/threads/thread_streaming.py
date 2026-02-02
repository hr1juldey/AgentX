"""Streaming execution logic for LangGraph threads.

This is a facade that re-exports streaming functionality from split components.
"""

from typing import AsyncGenerator

from agentx.presentation.api.v1.threads.stream_initializer import (
    prepare_stream_state,
)
from agentx.presentation.api.v1.threads.stream_processor import (
    process_stream_chunks,
)


async def stream_graph_execution(
    thread_id: str,
    input_data: dict,
    config: dict | None = None,
) -> AsyncGenerator[str, None]:
    """Stream graph execution via SSE.

    Args:
        thread_id: Thread identifier
        input_data: Input data for graph execution
        config: Optional config for graph execution

    Yields:
        SSE event strings
    """
    thread, initial_state, compiled_graph = prepare_stream_state(
        thread_id,
        input_data,
    )

    async for event in process_stream_chunks(
        compiled_graph,
        initial_state,
        thread,
        config or {},
    ):
        yield event
