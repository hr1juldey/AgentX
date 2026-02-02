"""Voice service dependencies.

Provides voice gateway and text stream handler singletons.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agentx.infrastructure.external.text_stream_handler import (
        TextStreamHandler,
    )
    from agentx.infrastructure.external.voice_gateway_service import (
        VoiceGatewayService,
    )


# Global singleton states
_voice_gateway_service: "VoiceGatewayService | None" = None
_text_stream_handler: "TextStreamHandler | None" = None


def get_text_stream_handler() -> "TextStreamHandler":
    """Get the text stream handler singleton.

    Returns:
        TextStreamHandler: The text stream handler instance.
    """
    global _text_stream_handler
    if _text_stream_handler is None:
        from agentx.infrastructure.external.text_stream_handler import (
            TextStreamHandler,
        )

        _text_stream_handler = TextStreamHandler()
    return _text_stream_handler


def get_voice_gateway_service() -> "VoiceGatewayService":
    """Get the voice gateway service singleton.

    Returns:
        VoiceGatewayService: The voice gateway service instance.
    """
    global _voice_gateway_service
    if _voice_gateway_service is None:
        from agentx.core.config import get_settings
        from agentx.infrastructure.external.voice_gateway_service import (
            VoiceGatewayConfig,
            VoiceGatewayService,
        )

        from agentx.core.dependency_facades.application import (
            get_conversation_state_manager,
        )

        settings = get_settings()
        state_manager = get_conversation_state_manager()
        text_handler = get_text_stream_handler()

        config = VoiceGatewayConfig(
            stt_url=settings.voice.kyutai_stt_url,
            tts_url=settings.voice.kyutai_tts_url,
        )
        _voice_gateway_service = VoiceGatewayService(
            config=config, state_manager=state_manager, text_handler=text_handler
        )
    return _voice_gateway_service


def reset_voice_dependencies() -> None:
    """Reset voice dependency singletons.

    Useful for testing or clearing state.
    """
    global _voice_gateway_service, _text_stream_handler
    _voice_gateway_service = None
    _text_stream_handler = None
