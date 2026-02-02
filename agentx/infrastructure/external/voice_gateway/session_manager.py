"""Voice gateway session management.

Handles session lifecycle and health checks.
"""

import logging
from typing import TYPE_CHECKING
from uuid import UUID

import websockets
from fastapi import WebSocket

from agentx.infrastructure.external.voice_gateway_models import VoiceSession
from agentx.infrastructure.external.voice_gateway_session_manager import (
    check_kyutai_health,
    cleanup_session,
)
from agentx.infrastructure.external.voice_protocol import create_config_message

if TYPE_CHECKING:
    from agentx.infrastructure.external.text_stream_handler import TextStreamHandler

logger = logging.getLogger(__name__)


async def create_session_connections(
    session_id: UUID,
    frontend_ws: WebSocket,
    stt_url: str,
    tts_url: str,
    sessions: dict[UUID, VoiceSession],
) -> VoiceSession:
    """Create WebSocket connections for STT and TTS.

    Args:
        session_id: The session identifier
        frontend_ws: Frontend WebSocket connection
        stt_url: STT server URL
        tts_url: TTS server URL
        sessions: Sessions dictionary to store the session

    Returns:
        VoiceSession: The created voice session
    """
    logger.info(f"[VoiceGateway] Connecting to STT: {stt_url}")
    stt_ws = await websockets.connect(stt_url)
    logger.info("[VoiceGateway] Connected to STT")

    logger.info(f"[VoiceGateway] Connecting to TTS: {tts_url}")
    tts_ws = await websockets.connect(tts_url)
    logger.info("[VoiceGateway] Connected to TTS")

    config_msg = create_config_message(session_id, streaming_mode="both")
    logger.info(f"[VoiceGateway] Sending config to STT: {config_msg.to_json()}")
    await stt_ws.send(config_msg.to_json())
    logger.info("[VoiceGateway] Config sent to STT")

    logger.info("[VoiceGateway] Sending config to TTS")
    await tts_ws.send(config_msg.to_json())
    logger.info("[VoiceGateway] Config sent to TTS")

    session = VoiceSession(
        session_id=session_id,
        frontend_ws=frontend_ws,
        stt_ws=stt_ws,
        tts_ws=tts_ws,
    )
    sessions[session_id] = session
    logger.info("[VoiceGateway] Session created")

    return session


async def cleanup_voice_session(
    session_id: UUID,
    sessions: dict[UUID, VoiceSession],
    text_handler: "TextStreamHandler | None" = None,
) -> None:
    """Clean up a voice session.

    Args:
        session_id: The session identifier
        sessions: Sessions dictionary
        text_handler: Text stream handler for cleanup
    """
    logger.info(f"[VoiceGateway] Cleaning up session {session_id}")
    await cleanup_session(session_id, sessions, text_handler)


async def check_server_health(stt_url: str) -> bool:
    """Check if kyutai server is available.

    Args:
        stt_url: STT server URL

    Returns:
        bool: True if server is healthy
    """
    return await check_kyutai_health(stt_url)
