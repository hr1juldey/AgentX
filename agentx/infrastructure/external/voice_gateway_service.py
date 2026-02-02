"""Voice gateway service for external kyutai integration.

Actual implementation has been moved to the voice_gateway/ subdirectory.
This facade maintains backward compatibility with existing imports.
"""

import asyncio
import logging
from typing import TYPE_CHECKING
from uuid import UUID

from fastapi import WebSocket

from agentx.core.config import get_settings
from agentx.infrastructure.external.voice_gateway import (
    VoiceGatewayError,
    check_server_health,
    cleanup_voice_session,
    create_config,
    create_session_connections,
    process_agent_callback,
    run_input_task,
    run_output_task,
)
from agentx.infrastructure.external.voice_gateway_models import VoiceSession

if TYPE_CHECKING:
    from agentx.application.use_cases.conversation_state_manager import (
        ConversationStateManager,
    )
    from agentx.infrastructure.external.text_stream_handler import TextStreamHandler
    from agentx.infrastructure.external.voice_gateway_models import (
        VoiceGatewayConfig,
    )

logger = logging.getLogger(__name__)
settings = get_settings()


class VoiceGatewayService:
    """Gateway for routing messages between frontend and kyutai voice-server."""

    def __init__(
        self,
        config: "VoiceGatewayConfig | None" = None,
        state_manager: "ConversationStateManager | None" = None,
        text_handler: "TextStreamHandler | None" = None,
    ) -> None:
        """Initialize voice gateway service."""
        from agentx.application.use_cases.conversation_state_manager import (
            ConversationStateManager,
        )
        from agentx.infrastructure.external.text_stream_handler import TextStreamHandler

        self._config = create_config(config)
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
        await create_session_connections(
            session_id,
            frontend_ws,
            self._config.stt_url,
            self._config.tts_url,
            self._sessions,
        )

        try:
            session = self._sessions[session_id]
            await asyncio.gather(
                run_input_task(session, self._text_handler),
                run_output_task(session, self._state_manager, self._text_handler),
            )
        except Exception as e:
            logger.error(f"[VoiceGateway] Error in session tasks: {e}", exc_info=True)
            raise
        finally:
            await cleanup_voice_session(session_id, self._sessions, self._text_handler)

    def _agent_callback(self, user_text: str) -> str:
        """Callback for processing STT results through agent."""
        return asyncio.run(process_agent_callback(user_text, self._state_manager))

    async def check_health(self) -> bool:
        """Check if kyutai server is available."""
        return await check_server_health(self._config.stt_url)


__all__ = ["VoiceGatewayService", "VoiceGatewayError"]
