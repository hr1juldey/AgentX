"""Voice gateway session management utilities."""

import logging
from typing import TYPE_CHECKING
from uuid import UUID

import websockets

from agentx.infrastructure.external.voice_gateway_models import VoiceSession

if TYPE_CHECKING:
    from agentx.infrastructure.external.text_stream_handler import TextStreamHandler

logger = logging.getLogger(__name__)


async def cleanup_session(
    session_id: UUID,
    sessions: dict[UUID, VoiceSession],
    text_handler: "TextStreamHandler | None" = None,
) -> None:
    """Clean up a voice session.

    Args:
        session_id: The session ID to clean up.
        sessions: The sessions dictionary to remove from.
        text_handler: The text handler for cleanup (optional).
    """
    session = sessions.pop(session_id, None)
    if session:
        if session.stt_ws:
            await session.stt_ws.close()  # type: ignore[union-attr]
        if session.tts_ws:
            await session.tts_ws.close()  # type: ignore[union-attr]
    # Clean up text handler state if provided
    if text_handler:
        text_handler.cleanup_session(session_id)


async def check_kyutai_health(stt_url: str) -> bool:
    """Check if kyutai server is available.

    Args:
        stt_url: The STT WebSocket URL to check.

    Returns:
        True if kyutai server is available, False otherwise.
    """
    try:
        async with websockets.connect(stt_url) as _:
            return True
    except Exception:
        return False
