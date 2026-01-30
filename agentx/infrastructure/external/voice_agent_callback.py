"""Agent response processing for voice gateway.

Provides callback functions for processing STT results through agents.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from agentx.application.dtos.voice_gateway_dtos import KyutaiMessage, KyutaiMessageType

if TYPE_CHECKING:
    from uuid import UUID

    from agentx.application.use_cases.conversation_state_manager import (
        ConversationStateManager,
    )
    from agentx.infrastructure.external.text_stream_handler import TextStreamHandler


def process_agent_response(user_text: str) -> str:
    """Process user text through agent and return response.

    Args:
        user_text: Transcribed user input

    Returns:
        Agent response text

    TODO: Integrate with C003 agent pipeline
    For now, echo the response.
    """
    return f"You said: {user_text}"


async def process_agent_response_with_tts(
    session_id: "UUID",
    user_text: str,
    state_manager: "ConversationStateManager",
    text_handler: "TextStreamHandler",
    tts_ws: Any,
) -> None:
    """Process user text through agent and send TTS response.

    Args:
        session_id: The session UUID
        user_text: The transcribed user input
        state_manager: The conversation state manager
        text_handler: The text stream handler
        tts_ws: The TTS WebSocket connection

    TODO: Integrate with C003 agent pipeline
    For now, echo the response.
    """
    # Track user message
    state_manager.add_user_message(session_id, user_text)

    # TODO: Integrate with C003 agent pipeline
    # For now, echo the response
    agent_response = f"You said: {user_text}"

    # Track assistant message
    state_manager.add_assistant_message(session_id, agent_response)

    # Stream TTS with sentence splitting
    async def send_sentence(sentence: str) -> None:
        """Send a sentence to TTS."""
        tts_message = KyutaiMessage(
            type=KyutaiMessageType.TEXT,
            data={"text": sentence, "action": "speak"},
            sessionId=str(session_id),
            timestamp=datetime.now(timezone.utc).timestamp(),
        )
        await tts_ws.send(tts_message.to_json())

    await text_handler.stream_tts_sentences(session_id, agent_response, send_sentence)
