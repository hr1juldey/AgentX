"""Domain models for voice subgraph state.

This module defines the VoiceState TypedDict for the TTS/STT
voice subgraph with guaranteed cleanup.
"""

from typing import Literal, TypedDict


class VoiceState(TypedDict):
    """Voice session state for TTS/STT subgraph.

    This state manages voice interactions with guaranteed cleanup
    for all WebSocket connections (STT, TTS, frontend).
    """

    # Session identifiers
    session_id: str
    user_id: str

    # WebSocket connection status (managed outside state)
    stt_connected: bool
    tts_connected: bool
    frontend_connected: bool

    # Audio streams
    audio_input_buffer: list[bytes]
    audio_output_buffer: list[bytes]

    # Transcription and synthesis
    transcribed_text: str
    synthesis_pending: bool
    synthesis_interrupted: bool

    # Agent communication
    agent_response: str

    # Status tracking
    current_step: Literal[
        "connect_kyutai",
        "listen_audio",
        "transcribe",
        "process_agent",
        "synthesize",
        "stream_audio",
        "check_interrupt",
        "cleanup",
    ]

    # Error handling
    error_message: str | None
    should_terminate: bool
