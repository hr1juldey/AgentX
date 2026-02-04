"""Voice SDK adapter - thin wrapper around libs/voice_client/ SDK."""

from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from voice_client import VoiceClient
else:
    from voice_client import VoiceClient  # type: ignore[import]


class VoiceSDKAdapter:
    """Thin wrapper around voice_client SDK for AGENTX integration."""

    def __init__(self, stt_url: str, tts_url: str) -> None:
        """Initialize the voice SDK adapter.

        Args:
            stt_url: STT WebSocket URL
            tts_url: TTS WebSocket URL
        """
        self.stt_url = stt_url
        self.tts_url = tts_url
        self._client: VoiceClient | None = None

    async def handle_session(
        self, websocket: object, session_id: str, agent_callback: Callable
    ) -> None:
        """Handle voice session using SDK's VoiceClient.converse_stream().

        Args:
            websocket: WebSocket connection
            session_id: Session identifier
            agent_callback: Agent callback function

        Raises:
            NotImplementedError: If not yet implemented
        """
        raise NotImplementedError(
            "VoiceSDKAdapter.handle_session() not yet implemented"
        )
