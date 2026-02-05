"""Voice service management (SDK adapter and gateway)."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

from agentx.core.config import settings

if TYPE_CHECKING:
    from agentx.infrastructure.voice.voice_adapter import VoiceSDKAdapter
    from agentx.infrastructure.voice.voice_gateway import VoiceGatewayService

logger = logging.getLogger(__name__)

_voice_sdk_adapter: Optional[VoiceSDKAdapter] = None
_voice_gateway: Optional[VoiceGatewayService] = None


def get_voice_sdk_adapter() -> VoiceSDKAdapter:
    """Get the singleton VoiceSDKAdapter."""
    from agentx.infrastructure.voice.voice_adapter import VoiceSDKAdapter

    global _voice_sdk_adapter
    if _voice_sdk_adapter is None:
        _voice_sdk_adapter = VoiceSDKAdapter(
            stt_url=settings.voice_kyutai_stt_url,
            tts_url=settings.voice_kyutai_tts_url,
        )
        logger.info("VoiceSDKAdapter initialized")
    return _voice_sdk_adapter


def get_voice_gateway() -> VoiceGatewayService:
    """Get the singleton VoiceGatewayService."""
    from agentx.core.sessions import get_session_manager as _get_session_manager
    from agentx.infrastructure.voice.voice_gateway import VoiceGatewayService

    global _voice_gateway
    if _voice_gateway is None:
        _voice_gateway = VoiceGatewayService(
            session_manager=_get_session_manager(),
            voice_adapter=get_voice_sdk_adapter(),
        )
        logger.info("VoiceGatewayService initialized")
    return _voice_gateway
