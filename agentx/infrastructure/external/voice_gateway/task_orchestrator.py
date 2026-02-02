"""Voice gateway task orchestration.

Handles input/output task coordination.
"""

import logging
from typing import TYPE_CHECKING

from agentx.infrastructure.external.voice_gateway_models import VoiceSession
from agentx.infrastructure.external.voice_session_tasks import (
    input_task,
    output_task,
)

if TYPE_CHECKING:
    from agentx.application.use_cases.conversation_state_manager import (
        ConversationStateManager,
    )
    from agentx.infrastructure.external.text_stream_handler import TextStreamHandler

logger = logging.getLogger(__name__)


async def run_input_task(
    session: VoiceSession, text_handler: "TextStreamHandler"
) -> None:
    """Handle messages from frontend to kyutai.

    Args:
        session: The active voice session
        text_handler: Text stream handler
    """
    await input_task(
        session.frontend_ws,
        session.session_id,
        session.stt_ws,  # type: ignore[arg-type]
        session.tts_ws,  # type: ignore[arg-type]
        text_handler,
    )


async def run_output_task(
    session: VoiceSession,
    state_manager: "ConversationStateManager",
    text_handler: "TextStreamHandler",
) -> None:
    """Handle messages from kyutai to frontend.

    Args:
        session: The active voice session
        state_manager: Conversation state manager
        text_handler: Text stream handler
    """
    from agentx.infrastructure.external.voice_gateway.agent_callback import (
        process_agent_response_with_tts,
    )

    async def _process_response(user_text: str) -> None:
        await process_agent_response_with_tts(
            session, user_text, state_manager, text_handler
        )

    await output_task(
        session.frontend_ws,
        session.session_id,
        session.stt_ws,  # type: ignore[arg-type]
        session.tts_ws,  # type: ignore[arg-type]
        state_manager,
        text_handler,
        _process_response,
    )
