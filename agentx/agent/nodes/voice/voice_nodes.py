"""Voice nodes for TTS/STT subgraph with guaranteed cleanup.

This module contains the nodes for voice session management.
All paths lead to cleanup, preventing WebSocket leaks.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


async def connect_kyutai_node(state: dict) -> dict:
    """Connect to Kyutai STT and TTS WebSocket servers.

    Args:
        state: Voice state

    Returns:
        dict: Updated state with connection status
    """
    # TODO: Implement actual WebSocket connections
    # For now, simulate successful connection
    stt_connected = True
    tts_connected = True

    if not stt_connected or not tts_connected:
        return {
            "error_message": "Failed to connect to Kyutai servers",
            "should_terminate": True,
            "current_step": "cleanup",
        }

    return {
        "stt_connected": True,
        "tts_connected": True,
        "current_step": "listen_audio",
    }


async def listen_audio_node(state: dict) -> dict:
    """Listen for audio input from frontend.

    Args:
        state: Voice state

    Returns:
        dict: Updated state with audio buffer
    """
    # TODO: Implement actual audio receiving
    # For now, simulate receiving audio
    return {
        "current_step": "transcribe",
    }


async def transcribe_node(state: dict) -> dict:
    """Transcribe audio to text using Kyutai STT.

    Args:
        state: Voice state

    Returns:
        dict: Updated state with transcribed text
    """
    # TODO: Implement actual STT via Kyutai
    # TODO: Use actual audio_buffer when implemented
    # For now, mock transcription
    transcribed = "Hello, this is a test transcription."

    return {
        "transcribed_text": transcribed,
        "current_step": "process_agent",
        "audio_input_buffer": [],
    }


async def process_agent_node(state: dict) -> dict:
    """Process transcribed text through main agent graph.

    Args:
        state: Voice state

    Returns:
        dict: Updated state with agent response
    """
    transcribed = state.get("transcribed_text", "")

    # TODO: Invoke main agent graph
    # For now, mock response
    response = f"I heard: {transcribed}"

    return {
        "agent_response": response,
        "synthesis_pending": True,
        "current_step": "synthesize",
    }


async def synthesize_node(state: dict) -> dict:
    """Synthesize agent response to audio using Kyutai TTS.

    Args:
        state: Voice state

    Returns:
        dict: Updated state with audio output
    """
    # TODO: Implement actual TTS via Kyutai
    # TODO: Use actual agent_response when implemented
    # For now, mock synthesis
    audio_chunks = [b"mock_audio_data"]

    return {
        "audio_output_buffer": audio_chunks,
        "synthesis_pending": False,
        "current_step": "stream_audio",
    }


async def stream_audio_node(state: dict) -> dict:
    """Stream audio output to frontend.

    Args:
        state: Voice state

    Returns:
        dict: Updated state
    """
    # TODO: Implement actual streaming
    # TODO: Use actual audio_buffer when implemented
    # For now, clear buffer

    return {
        "audio_output_buffer": [],
        "current_step": "check_interrupt",
    }


async def check_interrupt_node(state: dict) -> dict:
    """Check if user interrupted or session should continue.

    Args:
        state: Voice state

    Returns:
        dict: Updated state with next step
    """
    # TODO: Implement actual interrupt detection
    # For now, continue to cleanup

    return {
        "synthesis_interrupted": True,
        "current_step": "cleanup",
    }


async def cleanup_node(state: dict) -> dict:
    """CLEANUP NODE: Always runs, even on errors.

    CRITICAL: This node MUST run to prevent WebSocket leaks.

    Args:
        state: Voice state

    Returns:
        dict: Cleaned state
    """
    # TODO: Use session_id when implementing cleanup
    # Close STT WebSocket
    if state.get("stt_connected"):
        # TODO: Close actual STT WebSocket
        pass

    # Close TTS WebSocket
    if state.get("tts_connected"):
        # TODO: Close actual TTS WebSocket
        pass

    # Clear session state
    # TODO: Clear actual session state

    return {
        "stt_connected": False,
        "tts_connected": False,
        "audio_input_buffer": [],
        "audio_output_buffer": [],
        "current_step": "cleanup",
        "should_terminate": True,
    }
