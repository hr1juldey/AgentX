"""Voice gateway service for external kyutai integration."""

import asyncio
import logging
from typing import TYPE_CHECKING
from uuid import UUID

import websockets
from fastapi import WebSocket

from agentx.core.config import get_settings
from agentx.infrastructure.external.voice_gateway_models import (
    VoiceGatewayConfig,
    VoiceSession,
)
from agentx.infrastructure.external.voice_gateway_session_manager import (
    check_kyutai_health,
    cleanup_session,
)
from agentx.infrastructure.external.voice_protocol import create_config_message
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
settings = get_settings()


class VoiceGatewayError(Exception):
    """Voice gateway error."""


class VoiceGatewayService:
    """Gateway for routing messages between frontend and kyutai voice-server."""

    def __init__(
        self,
        config: VoiceGatewayConfig | None = None,
        state_manager: "ConversationStateManager | None" = None,
        text_handler: "TextStreamHandler | None" = None,
    ) -> None:
        """Initialize voice gateway service."""
        from agentx.application.use_cases.conversation_state_manager import (
            ConversationStateManager,
        )
        from agentx.infrastructure.external.text_stream_handler import TextStreamHandler

        self._config = config or VoiceGatewayConfig(
            use_voice_sdk=settings.voice.use_voice_sdk
        )
        self._sessions: dict[UUID, VoiceSession] = {}
        self._state_manager = state_manager or ConversationStateManager()
        self._text_handler = text_handler or TextStreamHandler()

    async def handle_session(self, frontend_ws: WebSocket, session_id: UUID) -> None:
        """Handle a voice session WebSocket connection."""
        logger.info(f"[VoiceGateway] Starting session {session_id}")

        if len(self._sessions) >= self._config.max_concurrent_sessions:
            raise VoiceGatewayError("Max concurrent sessions reached")

        # Create or get conversation session
        self._state_manager.get_or_create_session(session_id)

        # Use VoiceSDKAdapter if feature flag is enabled
        if self._config.use_voice_sdk:
            from agentx.infrastructure.external.voice_sdk_adapter import VoiceSDKAdapter

            logger.info(f"Using voice_client SDK for session {session_id}")
            adapter = VoiceSDKAdapter(
                use_sdk=True,
                stt_url=self._config.stt_url,
                tts_url=self._config.tts_url,
            )
            await adapter.handle_session(
                frontend_ws,
                session_id,
                agent_callback=self._agent_callback,
                state_manager=self._state_manager,
                text_handler=self._text_handler,
            )
            return

        # Direct WebSocket mode (original implementation)
        logger.info(f"[VoiceGateway] Connecting to STT: {self._config.stt_url}")
        stt_ws = await websockets.connect(self._config.stt_url)
        logger.info(f"[VoiceGateway] Connected to STT")

        logger.info(f"[VoiceGateway] Connecting to TTS: {self._config.tts_url}")
        tts_ws = await websockets.connect(self._config.tts_url)
        logger.info(f"[VoiceGateway] Connected to TTS")

        config_msg = create_config_message(session_id, streaming_mode="both")
        logger.info(f"[VoiceGateway] Sending config to STT: {config_msg.to_json()}")
        await stt_ws.send(config_msg.to_json())
        logger.info(f"[VoiceGateway] Config sent to STT")

        logger.info(f"[VoiceGateway] Sending config to TTS")
        await tts_ws.send(config_msg.to_json())
        logger.info(f"[VoiceGateway] Config sent to TTS")

        session = VoiceSession(
            session_id=session_id,
            frontend_ws=frontend_ws,
            stt_ws=stt_ws,
            tts_ws=tts_ws,
        )
        self._sessions[session_id] = session
        logger.info(f"[VoiceGateway] Session created, starting input/output tasks")

        try:
            await asyncio.gather(
                self._input_task(session),
                self._output_task(session),
            )
        except Exception as e:
            logger.error(f"[VoiceGateway] Error in session tasks: {e}", exc_info=True)
            raise
        finally:
            logger.info(f"[VoiceGateway] Cleaning up session {session_id}")
            await cleanup_session(session_id, self._sessions, self._text_handler)

    def _agent_callback(self, user_text: str) -> str:
        """Callback for processing STT results through agent.

        Args:
            user_text: Transcribed user input

        Returns:
            Agent response text
        """
        from agentx.infrastructure.external.voice_agent_callback import (
            process_agent_response,
        )

        return process_agent_response(user_text)

    async def _input_task(self, session: VoiceSession) -> None:
        """Handle messages from frontend to kyutai."""
        await input_task(
            session.frontend_ws,
            session.session_id,
            session.stt_ws,  # type: ignore[arg-type]
            session.tts_ws,  # type: ignore[arg-type]
            self._text_handler,
        )

    async def _output_task(self, session: VoiceSession) -> None:
        """Handle messages from kyutai to frontend."""
        await output_task(
            session.frontend_ws,
            session.session_id,
            session.stt_ws,  # type: ignore[arg-type]
            session.tts_ws,  # type: ignore[arg-type]
            self._state_manager,
            self._text_handler,
            self._process_agent_response,
        )

    async def _process_agent_response(
        self, session: VoiceSession, user_text: str
    ) -> None:
        """Process user text through C003 agent and send response to TTS.

        Args:
            session: The active voice session.
            user_text: The transcribed user input.
        """
        from agentx.infrastructure.external.voice_agent_callback import (
            process_agent_response_with_tts,
        )

        await process_agent_response_with_tts(
            session.session_id,
            user_text,
            self._state_manager,
            self._text_handler,
            session.tts_ws,  # type: ignore[arg-type]
        )

    async def check_health(self) -> bool:
        """Check if kyutai server is available."""
        return await check_kyutai_health(self._config.stt_url)
