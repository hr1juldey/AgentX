"""Voice SDK adapter for hybrid SDK + direct WebSocket pattern.

Wraps voice_client SDK as internal dependency while maintaining AgentX's
public API and providing fallback to direct WebSocket implementation.
"""

import logging
from typing import TYPE_CHECKING

from agentx.core.config import get_settings

if TYPE_CHECKING:
    from collections.abc import Callable
    from uuid import UUID

    from fastapi import WebSocket
    from voice_client.voice import VoiceClient


logger = logging.getLogger(__name__)
settings = get_settings()


class VoiceSDKAdapter:
    """Adapter for voice_client SDK with direct WebSocket fallback.

    Provides hybrid approach:
    - Uses voice_client SDK internally for reconnection, encoding, audio handling
    - Falls back to direct WebSocket if SDK unavailable or disabled
    - Maintains AgentX DTOs as public API (KyutaiMessage, etc.)
    - Maps SDK sessions to AgentX conversation IDs

    Attributes:
        _use_sdk: Whether to use SDK (from settings.voice.use_voice_sdk)
        _stt_url: STT WebSocket URL from settings
        _tts_url: TTS WebSocket URL from settings
        _sdk_to_agentx_sessions: Maps SDK session IDs to AgentX conversation IDs
    """

    def __init__(
        self,
        use_sdk: bool = False,
        stt_url: str | None = None,
        tts_url: str | None = None,
    ) -> None:
        """Initialize the voice SDK adapter.

        Args:
            use_sdk: Whether to use voice_client SDK (default: false)
            stt_url: Optional STT WebSocket URL (defaults to settings)
            tts_url: Optional TTS WebSocket URL (defaults to settings)
        """
        self._use_sdk = use_sdk
        self._stt_url = stt_url or settings.voice.kyutai_stt_url
        self._tts_url = tts_url or settings.voice.kyutai_tts_url
        self._sdk_to_agentx_sessions: dict[str, UUID] = {}

    def _init_sdk_client(self) -> VoiceClient | None:
        """Initialize voice_client SDK VoiceClient.

        Returns:
            VoiceClient instance if available, None otherwise
        """
        if not self._use_sdk:
            logger.debug("SDK disabled, will use direct WebSocket")
            return None

        try:
            from voice_client import VoiceClient

            logger.debug(f"Initializing SDK: STT={self._stt_url}, TTS={self._tts_url}")
            return VoiceClient(stt_url=self._stt_url, tts_url=self._tts_url)
        except ImportError:
            logger.warning("voice_client SDK not available, using direct WebSocket")
            return None

    def _map_sdk_session_to_agentx(
        self, sdk_session_id: str, agentx_session_id: UUID
    ) -> None:
        """Map SDK session ID to AgentX conversation ID.

        Args:
            sdk_session_id: The SDK's session ID (string UUID)
            agentx_session_id: AgentX's conversation session ID
        """
        self._sdk_to_agentx_sessions[sdk_session_id] = agentx_session_id
        logger.debug(
            f"Mapped SDK session {sdk_session_id} to AgentX session {agentx_session_id}"
        )

    async def handle_session(
        self,
        frontend_ws: WebSocket,
        session_id: UUID,
        agent_callback: Callable[[str], str] | None = None,
        state_manager: object = None,
        text_handler: object = None,
    ) -> None:
        """Handle a voice session with SDK or direct WebSocket.

        Args:
            frontend_ws: The frontend WebSocket connection
            session_id: AgentX conversation session ID
            agent_callback: Optional callback for processing STT results
            state_manager: Optional ConversationStateManager for direct WS mode
            text_handler: Optional TextStreamHandler for direct WS mode
        """
        from agentx.infrastructure.external.voice_direct_fallback import (
            VoiceDirectFallback,
        )
        from agentx.infrastructure.external.voice_sdk_handler import VoiceSDKHandler

        sdk_client = self._init_sdk_client()

        if sdk_client:
            # Use SDK mode (requires async context manager)
            try:
                async with sdk_client:
                    sdk_handler = VoiceSDKHandler(self)
                    await sdk_handler.handle_via_sdk(
                        sdk_client, frontend_ws, session_id, agent_callback
                    )
            except Exception as e:
                logger.error(f"SDK session failed: {e}")
                # Fallback to direct WebSocket on SDK error
                logger.info("Falling back to direct WebSocket")
                direct_fallback = VoiceDirectFallback(self)
                await direct_fallback.handle_via_direct_ws(
                    frontend_ws, session_id, agent_callback, state_manager, text_handler
                )
        else:
            # Use direct WebSocket mode
            direct_fallback = VoiceDirectFallback(self)
            await direct_fallback.handle_via_direct_ws(
                frontend_ws, session_id, agent_callback, state_manager, text_handler
            )
