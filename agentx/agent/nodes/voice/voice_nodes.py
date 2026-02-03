"""Voice nodes for TTS/STT subgraph with guaranteed cleanup.

This module re-exports all voice nodes for backwards compatibility.
All paths lead to cleanup, preventing WebSocket leaks.
"""

from agentx.agent.nodes.voice.voice_input_nodes import (
    connect_kyutai_node,
    listen_audio_node,
    transcribe_node,
)
from agentx.agent.nodes.voice.voice_output_nodes import (
    check_interrupt_node,
    cleanup_node,
    process_agent_node,
    stream_audio_node,
    synthesize_node,
)

__all__ = [
    # Input nodes
    "connect_kyutai_node",
    "listen_audio_node",
    "transcribe_node",
    # Output nodes
    "process_agent_node",
    "synthesize_node",
    "stream_audio_node",
    "check_interrupt_node",
    "cleanup_node",
]
