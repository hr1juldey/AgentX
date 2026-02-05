"""Basic conversation support (STT → Agent → TTS)."""

import asyncio
from typing import Any


class BasicConversationMixin:
    """Provides basic non-streaming conversation methods."""

    async def converse(
        self,
        audio: str | bytes,
        agent_callback: Any = None,
    ) -> tuple[str, bytes]:
        """Full conversation: STT → Agent → TTS.

        Args:
            audio: User speech input (file path or bytes)
            agent_callback: Optional function to process transcription and return response

        Returns:
            Tuple of (transcription, response_audio)

        Raises:
            Exception: Propagates any errors from STT or TTS
        """
        # Step 1: Transcribe
        transcription = await self.stt.transcribe(audio)

        # Step 2: Process with agent
        if agent_callback:
            if asyncio.iscoroutinefunction(agent_callback):
                response_text = await agent_callback(transcription)
            else:
                response_text = agent_callback(transcription)
        else:
            response_text = f"You said: {transcription}"

        # Step 3: Synthesize response
        response_audio = await self.tts.synthesize_full(response_text)

        return transcription, response_audio
