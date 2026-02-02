"""Stream processing utilities for LangGraph threads.

Handles chunk processing and event generation during streaming.
"""

from typing import AsyncGenerator

from agentx.agent.state import AgentState
from agentx.presentation.api.v1.threads.thread_manager import generate_event


async def process_stream_chunks(
    compiled_graph: object,  # type: ignore[valid-type]
    initial_state: AgentState,
    thread: dict,
    config: dict,
) -> AsyncGenerator[str, None]:
    """Process graph execution chunks and generate SSE events.

    Args:
        compiled_graph: Compiled LangGraph for execution
        initial_state: Initial state for graph execution
        thread: Thread dictionary to update
        config: Optional config for graph execution

    Yields:
        SSE event strings
    """
    try:
        async for chunk in compiled_graph.astream(  # type: ignore[call-arg]
            initial_state,
            config=config,
        ):
            # Update thread state
            if isinstance(chunk, dict):
                thread["state"].update(chunk)  # type: ignore[arg-type]

            # Send UI update events
            if isinstance(chunk, dict) and "ui" in chunk:
                for ui_msg in chunk.get("ui", []):
                    yield generate_event(
                        "custom",
                        {
                            "name": ui_msg.get("name", "ui_component"),
                            "args": ui_msg,
                        },
                    )

            # Send message partial events
            if isinstance(chunk, dict) and "messages" in chunk:
                messages = chunk["messages"]
                if messages:
                    latest_msg = messages[-1]
                    if hasattr(latest_msg, "content"):
                        yield generate_event(
                            "messages/partial",
                            {
                                "messages": [
                                    {
                                        "role": "assistant",
                                        "content": str(latest_msg.content),
                                    }
                                ]
                            },
                        )

        # Update thread metadata
        from datetime import datetime, timezone

        thread["updated_at"] = datetime.now(timezone.utc).isoformat()

        # Send completion event
        yield generate_event(
            "messages/complete",
            {
                "messages": [
                    {
                        "role": msg.type if hasattr(msg, "type") else "ai",
                        "content": str(msg.content)
                        if hasattr(msg, "content")
                        else str(msg),
                    }
                    for msg in thread["state"].get("messages", [])
                ]
            },
        )

    except Exception as e:
        yield generate_event(
            "error",
            {
                "error": str(e),
                "message": "Graph execution failed",
            },
        )
