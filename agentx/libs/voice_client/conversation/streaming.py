"""Streaming conversation support with event emission."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

from voice_client.conversation.events import ConversationEvent

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from voice_client.stt import TranscriptionResult


class StreamingConversationMixin:
    """Provides streaming conversation methods with real-time events."""

    async def converse_stream(
        self,
        audio: str | bytes,
        agent_callback: Any = None,
    ) -> AsyncIterator[ConversationEvent]:
        """Stream conversation events in real-time.

        Args:
            audio: User speech input (file path or bytes)
            agent_callback: Optional function to process transcription

        Yields:
            ConversationEvent with updates
        """
        import time

        final_result: TranscriptionResult | None = None

        # Step 1: Stream STT
        async for result in self.stt.stream_transcription():
            if result.is_final:
                final_result = result
                event = ConversationEvent(
                    type="stt_final",
                    data=result,
                    timestamp=time.time(),
                )
                yield event
                break
            else:
                event = ConversationEvent(
                    type="stt_partial",
                    data=result,
                    timestamp=time.time(),
                )
                yield event

        # Make sure we have the final result
        if final_result is None:
            raise RuntimeError("STT stream ended without a final result")

        # Step 2: Process with agent
        transcription = final_result.text
        if agent_callback:
            if asyncio.iscoroutinefunction(agent_callback):
                response_text = await agent_callback(transcription)
            else:
                response_text = agent_callback(transcription)
        else:
            response_text = f"You said: {transcription}"

        # Step 3: Stream TTS
        async for chunk in self.tts.synthesize(response_text):
            event = ConversationEvent(
                type="tts_audio",
                data=chunk,
                timestamp=time.time(),
            )
            yield event

        # Complete
        event = ConversationEvent(
            type="complete",
            data=None,
            timestamp=time.time(),
        )
        yield event
