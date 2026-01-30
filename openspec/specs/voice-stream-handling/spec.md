# Spec: voice-stream-handling

**File**: `specs/voice-stream-handling/spec.md`

**Generated**: 2026-01-31
**Change**: c010-voice-client

---

## 1.1 Purpose

Define text stream handling for efficient processing of STT transcripts and TTS inputs. This spec covers buffering, debouncing, and sentence splitting for optimal performance and user experience.

---

## 1.2 Scope

**In Scope**:
- STT transcript buffering (partial → complete transcripts)
- TTS sentence splitting (complete responses → sentences)
- Audio chunk debouncing for network efficiency
- Interruption handling during TTS streaming

**Out of Scope**:
- WebSocket connection management (covered by voice-gateway spec)
- Audio processing (handled by kyutai)
- Conversation state (covered by conversational-state spec)

---

## 1.3 Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-VSH-001 | System MUST buffer STT transcripts until Eos or punctuation | Must |
| FR-VSH-002 | System MUST send complete transcripts to frontend and agent | Must |
| FR-VSH-003 | System MUST split TTS input into complete sentences | Must |
| FR-VSH-004 | System MUST send sentences to kyutai TTS sequentially | Must |
| FR-VSH-005 | System MUST handle interruption during TTS streaming | Must |
| FR-VSH-006 | System MUST debounce audio chunks (500ms window) | Should |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-VSH-001 | TextStreamHandler MUST use absolute imports only | Must |
| NFR-VSH-002 | TextStreamHandler MUST pass ruff check and ruff format | Must |
| NFR-VSH-003 | TextStreamHandler MUST pass pyrefly type checking | Must |
| NFR-VSH-004 | TextStreamHandler file MUST NOT exceed 150 lines | Must |
| NFR-VSH-005 | Buffer operations MUST complete within 10ms | Should |

---

## 1.4 Data Model

### File: agentx/infrastructure/external/text_stream_handler.py

```python
"""Text stream handler for voice interactions."""

import asyncio
import re
from dataclasses import dataclass, field
from typing import Awaitable, Callable
from uuid import UUID


@dataclass
class STTBuffer:
    """Buffer for STT transcripts.

    Attributes:
        session_id: Session identifier.
        chunks: List of transcript chunks.
        is_complete: Whether transcript is complete (Eos received).
    """

    session_id: UUID
    chunks: list[str] = field(default_factory=list)
    is_complete: bool = False

    def add_chunk(self, chunk: str) -> str | None:
        """Add a transcript chunk.

        Args:
            chunk: Transcript chunk to add.

        Returns:
            Complete transcript if buffer should flush, None otherwise.
        """
        self.chunks.append(chunk)

        # Flush on sentence-ending punctuation
        if chunk.rstrip()[-1:] in {".", "!", "?"}:
            return self.flush()

        return None

    def complete(self) -> str:
        """Mark buffer as complete and return final transcript.

        Returns:
            Complete transcript.
        """
        self.is_complete = True
        return self.flush()

    def flush(self) -> str:
        """Flush buffer and return transcript.

        Returns:
            Flushed transcript.
        """
        transcript = " ".join(self.chunks)
        self.chunks.clear()
        return transcript


class TextStreamHandler:
    """Handle text streaming for voice interactions.

    Buffers STT transcripts and splits TTS input into sentences.
    """

    def __init__(self) -> None:
        """Initialize text stream handler."""
        self._stt_buffers: dict[UUID, STTBuffer] = {}
        self._interrupted_sessions: set[UUID] = set()

    def buffer_stt_chunk(self, session_id: UUID, chunk: str) -> str | None:
        """Buffer an STT transcript chunk.

        Args:
            session_id: Session identifier.
            chunk: Transcript chunk.

        Returns:
            Complete transcript if buffer should flush, None otherwise.
        """
        if session_id not in self._stt_buffers:
            self._stt_buffers[session_id] = STTBuffer(session_id=session_id)

        buffer = self._stt_buffers[session_id]
        return buffer.add_chunk(chunk)

    def complete_stt_transcript(self, session_id: UUID) -> str:
        """Mark STT transcript as complete and return final transcript.

        Args:
            session_id: Session identifier.

        Returns:
            Complete transcript.
        """
        buffer = self._stt_buffers.get(session_id)
        if buffer:
            transcript = buffer.complete()
            del self._stt_buffers[session_id]
            return transcript
        return ""

    def split_tts_sentences(self, text: str) -> list[str]:
        """Split TTS input into complete sentences.

        Args:
            text: Input text.

        Returns:
            List of sentences.
        """
        # Split on sentence boundaries
        sentences = re.split(r"(?<=[.!?])\s+", text)

        # Filter empty strings
        return [s.strip() for s in sentences if s.strip()]

    async def stream_tts_sentences(
        self,
        session_id: UUID,
        text: str,
        send_callback: Callable[[str], Awaitable[None]],
    ) -> None:
        """Stream TTS sentences with interruption handling.

        Args:
            session_id: Session identifier.
            text: Text to synthesize.
            send_callback: Async callback to send each sentence.
        """
        sentences = self.split_tts_sentences(text)

        for sentence in sentences:
            # Check for interruption
            if session_id in self._interrupted_sessions:
                self._interrupted_sessions.remove(session_id)
                break

            # Send sentence to TTS
            await send_callback(sentence)

    def interrupt_tts(self, session_id: UUID) -> None:
        """Interrupt TTS streaming for a session.

        Args:
            session_id: Session identifier.
        """
        self._interrupted_sessions.add(session_id)

    def cleanup_session(self, session_id: UUID) -> None:
        """Clean up session state.

        Args:
            session_id: Session identifier.
        """
        self._stt_buffers.pop(session_id, None)
        self._interrupted_sessions.discard(session_id)
```

---

## 1.5 Acceptance Criteria

- [ ] STT transcripts buffer until Eos or punctuation
- [ ] Complete transcripts sent to frontend and agent
- [ ] TTS input split into complete sentences
- [ ] Sentences sent to kyutai TTS sequentially
- [ ] Interruption handled during TTS streaming
- [ ] Audio chunks debounced within 500ms window
- [ ] TextStreamHandler passes ruff check, ruff format, pyrefly check
- [ ] TextStreamHandler file under 150 lines

---

**Related Specs**:
- `voice-gateway` - Backend service for routing messages
- `conversational-state` - Conversation state management

---
