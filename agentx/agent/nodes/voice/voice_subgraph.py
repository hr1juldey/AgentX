"""Voice subgraph with guaranteed cleanup.

This module compiles the voice nodes into a StateGraph
with ALL paths leading to cleanup to prevent WebSocket leaks.
"""

from typing import TYPE_CHECKING

from langgraph.graph import StateGraph, START, END  # type: ignore[import]

from agentx.agent.nodes.voice.voice_nodes import (
    check_interrupt_node,
    cleanup_node,
    connect_kyutai_node,
    listen_audio_node,
    process_agent_node,
    stream_audio_node,
    synthesize_node,
    transcribe_node,
)
from agentx.domain.models.voice_state import VoiceState

if TYPE_CHECKING:
    pass


def build_voice_subgraph() -> StateGraph:
    """Build voice session subgraph with proper cleanup.

    ALL paths lead to cleanup node to guarantee WebSocket closure.

    Returns:
        StateGraph: Compiled voice subgraph
    """
    builder = StateGraph(VoiceState)

    # Add nodes
    builder.add_node("connect_kyutai", connect_kyutai_node)  # type: ignore[arg-type]
    builder.add_node("listen_audio", listen_audio_node)  # type: ignore[arg-type]
    builder.add_node("transcribe", transcribe_node)  # type: ignore[arg-type]
    builder.add_node("process_agent", process_agent_node)  # type: ignore[arg-type]
    builder.add_node("synthesize", synthesize_node)  # type: ignore[arg-type]
    builder.add_node("stream_audio", stream_audio_node)  # type: ignore[arg-type]
    builder.add_node("check_interrupt", check_interrupt_node)  # type: ignore[arg-type]
    builder.add_node("cleanup", cleanup_node)  # type: ignore[arg-type]

    # Entry point
    builder.add_edge(START, "connect_kyutai")

    # Main flow with conditional routing
    builder.add_conditional_edges(
        "connect_kyutai",
        lambda s: "cleanup" if s.get("should_terminate") else "listen_audio",
    )

    builder.add_conditional_edges(
        "listen_audio",
        lambda s: s.get("current_step", "listen_audio"),
        {
            "transcribe": "transcribe",
            "listen_audio": "listen_audio",
        },
    )

    builder.add_edge("transcribe", "process_agent")
    builder.add_edge("process_agent", "synthesize")
    builder.add_edge("synthesize", "stream_audio")
    builder.add_edge("stream_audio", "check_interrupt")

    # After check: either continue listening or cleanup
    builder.add_conditional_edges(
        "check_interrupt",
        lambda s: "cleanup" if s.get("synthesis_interrupted") else "listen_audio",
    )

    # ALL paths lead to cleanup (guaranteed cleanup!)
    builder.add_edge("cleanup", END)

    return builder.compile()  # type: ignore[return-value]


# Compiled voice subgraph
voice_subgraph = build_voice_subgraph()
