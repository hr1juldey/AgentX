"""Text stream handler for voice interactions."""

import re
from dataclasses import dataclass, field
from typing import Awaitable, Callable
from uuid import UUID


@dataclass
class STTBuffer:
    """Buffer for STT transcripts with auto-flush on punctuation."""

    session_id: UUID
    chunks: list[str] = field(default_factory=list)
    is_complete: bool = False

    def add_chunk(self, chunk: str) -> str | None:
        """Add chunk, return transcript if ends with .!? else None."""
        self.chunks.append(chunk)
        if chunk.rstrip()[-1:] in {".", "!", "?"}:
            return self.flush()
        return None

    def complete(self) -> str:
        """Mark complete and return final transcript."""
        self.is_complete = True
        return self.flush()

    def flush(self) -> str:
        """Flush and return transcript."""
        transcript = " ".join(self.chunks)
        self.chunks.clear()
        return transcript


class TextStreamHandler:
    """Handle text streaming: STT buffering and TTS sentence splitting."""

    def __init__(self) -> None:
        self._stt_buffers: dict[UUID, STTBuffer] = {}
        self._interrupted_sessions: set[UUID] = set()

    def buffer_stt_chunk(self, session_id: UUID, chunk: str) -> str | None:
        """Buffer STT chunk, return transcript if flush needed."""
        if session_id not in self._stt_buffers:
            self._stt_buffers[session_id] = STTBuffer(session_id=session_id)
        return self._stt_buffers[session_id].add_chunk(chunk)

    def complete_stt_transcript(self, session_id: UUID) -> str:
        """Mark STT complete and return final transcript."""
        buffer = self._stt_buffers.get(session_id)
        if buffer:
            transcript = buffer.complete()
            del self._stt_buffers[session_id]
            return transcript
        return ""

    def split_tts_sentences(self, text: str) -> list[str]:
        """Split text into sentences."""
        return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]

    async def stream_tts_sentences(
        self,
        session_id: UUID,
        text: str,
        send_callback: Callable[[str], Awaitable[None]],
    ) -> None:
        """Stream sentences with interruption handling."""
        for sentence in self.split_tts_sentences(text):
            if session_id in self._interrupted_sessions:
                self._interrupted_sessions.remove(session_id)
                break
            await send_callback(sentence)

    def interrupt_tts(self, session_id: UUID) -> None:
        """Interrupt TTS streaming."""
        self._interrupted_sessions.add(session_id)

    def cleanup_session(self, session_id: UUID) -> None:
        """Clean up session state."""
        self._stt_buffers.pop(session_id, None)
        self._interrupted_sessions.discard(session_id)
