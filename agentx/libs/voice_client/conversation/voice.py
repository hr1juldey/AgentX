"""Combined STT + TTS client for full conversations.

Provides a unified interface for speech-to-text transcription,
agent processing, and text-to-speech synthesis.
"""

import types
from typing import Any

from typing_extensions import Self

from agentx.libs.voice_client.conversation.basic import BasicConversationMixin
from agentx.libs.voice_client.conversation.streaming import StreamingConversationMixin
from agentx.libs.voice_client.stt import STTClient
from agentx.libs.voice_client.tts import TTSClient


class VoiceClient(BasicConversationMixin, StreamingConversationMixin):
    """Combined STT + TTS client for full conversations.

    Attributes:
        stt: The STT client instance
        tts: The TTS client instance
    """

    def __init__(
        self,
        stt_url: str | None = None,
        tts_url: str | None = None,
        url: str | None = None,
        api_key: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the voice client.

        Args:
            stt_url: Optional STT WebSocket URL
            tts_url: Optional TTS WebSocket URL
            url: Shared base URL (appends /stt and /tts)
            api_key: Optional API key for authentication
            **kwargs: Additional arguments passed to clients
        """
        # Handle URL construction
        if url and not (stt_url or tts_url):
            stt_url = url
            tts_url = url

        self.stt = STTClient(stt_url, api_key, **kwargs)
        self.tts = TTSClient(tts_url, api_key, **kwargs)

    async def __aenter__(self) -> Self:
        """Enter the async context manager.

        Returns:
            The connected voice client instance
        """
        try:
            await self.stt.__aenter__()
            await self.tts.__aenter__()
            return self
        except Exception:
            # If TTS connection fails, close STT connection
            await self.stt.__aexit__(None, None, None)
            raise

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None:
        """Exit the async context manager.

        Args:
            exc_type: Exception type
            exc_val: Exception value
            exc_tb: Exception traceback
        """
        await self.stt.__aexit__(exc_type, exc_val, exc_tb)
        await self.tts.__aexit__(exc_type, exc_val, exc_tb)
