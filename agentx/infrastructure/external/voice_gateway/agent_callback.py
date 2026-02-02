"""Voice gateway agent callback handling.

Processes STT results through agent and coordinates with TTS.
"""

import logging
from typing import TYPE_CHECKING

from agentx.infrastructure.external.voice_gateway_models import VoiceSession

if TYPE_CHECKING:
    from agentx.application.use_cases.conversation_state_manager import (
        ConversationStateManager,
    )
    from agentx.infrastructure.external.text_stream_handler import TextStreamHandler

logger = logging.getLogger(__name__)


async def process_agent_callback(
    user_text: str,
    state_manager: "ConversationStateManager",
) -> str:
    """Callback for processing STT results through agent.

    Args:
        user_text: Transcribed user input
        state_manager: Conversation state manager

    Returns:
        Agent response text
    """
    from agentx.infrastructure.external.voice_agent_callback import (
        process_agent_response,
    )

    return process_agent_response(user_text)


async def process_agent_response_with_tts(
    session: VoiceSession,
    user_text: str,
    state_manager: "ConversationStateManager",
    text_handler: "TextStreamHandler",
) -> None:
    """Process user text through C003 agent and send response to TTS.

    Args:
        session: The active voice session
        user_text: The transcribed user input
        state_manager: Conversation state manager
        text_handler: Text stream handler
    """
    from agentx.infrastructure.external.voice_agent_callback import (
        process_agent_response_with_tts as _process_with_tts,
    )

    await _process_with_tts(
        session.session_id,
        user_text,
        state_manager,
        text_handler,
        session.tts_ws,  # type: ignore[arg-type]
    )
