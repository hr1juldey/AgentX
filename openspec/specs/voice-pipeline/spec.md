# Spec: voice-pipeline

**File**: `specs/voice-pipeline/spec.md`

**Generated**: 2026-01-28
**Change**: c004-voice-streaming

---

## 1.1 Purpose

Define the streaming voice pipeline that orchestrates VAD filtering, STT transcription, LLM processing via C003 agent pipeline, and TTS synthesis. The pipeline supports full-duplex WebSocket communication with interruption handling.

---

## 1.2 Scope

**In Scope**:
- VoicePipelineUseCase orchestration (VAD → STT → LLM → TTS)
- WebSocket bidirectional streaming (separate input/output tasks)
- Audio chunk processing (500ms chunks for <300ms latency)
- Interruption handling (VAD monitoring during TTS)
- Session lifecycle management (create, process, terminate)
- Integration with C003 ExecuteAgentQueryUseCase

**Out of Scope**:
- Voice wake word detection (future feature)
- Speaker recognition (future feature)
- Multi-language support (English only)

---

## 1.3 Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-VOICE-001 | Pipeline MUST accept audio input at any sample rate and resample to 16kHz for STT | Must |
| FR-VOICE-002 | Pipeline MUST use VAD to filter silence before STT processing | Must |
| FR-VOICE-003 | Pipeline MUST stream TTS output in 500ms chunks | Must |
| FR-VOICE-004 | Pipeline MUST support full-duplex WebSocket (simultaneous input/output) | Must |
| FR-VOICE-005 | Pipeline MUST monitor VAD during TTS for interruption handling | Must |
| FR-VOICE-006 | Pipeline MUST integrate with C003 ExecuteAgentQueryUseCase for LLM processing | Must |
| FR-VOICE-007 | Pipeline MUST create and manage voice sessions with unique IDs | Must |
| FR-VOICE-008 | Pipeline MUST support graceful disconnection and cleanup | Must |
| FR-VOICE-009 | Pipeline MUST emit voice state UI updates via `push_ui_message()` | Must |
| FR-VOICE-010 | Voice nucleus widget MUST use 2D SVG metaballs for visual feedback | Must |
| FR-VOICE-011 | Interrupt button MUST be server-driven UI component | Should |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-VOICE-001 | End-to-end latency MUST be <500ms (P95), target <300ms (P50) | Must |
| NFR-VOICE-002 | Pipeline MUST support 5 concurrent sessions without degradation | Should |
| NFR-VOICE-003 | Memory usage MUST stay under 2GB after 1 hour of operation | Must |
| NFR-VOICE-004 | Interruption latency MUST be <200ms (P95) | Must |
| NFR-VOICE-005 | Pipeline MUST recover from WebSocket disconnection | Should |

---

## 1.4 Data Model

```python
# File: domain/entities/voice_session.py
from dataclasses import dataclass, field
from uuid import UUID
from datetime import datetime
from enum import Enum
from typing import Optional


class VoiceSessionState(str, Enum):
    """Voice session lifecycle states."""
    CREATED = "created"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    CLOSED = "closed"


@dataclass
class VoiceSessionEntity:
    """Voice session entity for tracking conversation state."""

    session_id: UUID
    state: VoiceSessionState
    created_at: datetime
    last_activity_at: datetime
    interrupted: bool = False
    audio_chunks_received: int = 0
    transcript: Optional[str] = None
    llm_response: Optional[str] = None

    def start_listening(self) -> None:
        """Transition to listening state."""
        self.state = VoiceSessionState.LISTENING
        self.last_activity_at = datetime.utcnow()

    def start_processing(self) -> None:
        """Transition to processing state."""
        self.state = VoiceSessionState.PROCESSING
        self.last_activity_at = datetime.utcnow()

    def start_speaking(self) -> None:
        """Transition to speaking state."""
        self.state = VoiceSessionState.SPEAKING
        self.last_activity_at = datetime.utcnow()

    def interrupt(self) -> None:
        """Mark session as interrupted."""
        self.interrupted = True
        self.last_activity_at = datetime.utcnow()

    def close(self) -> None:
        """Close the session."""
        self.state = VoiceSessionState.CLOSED
        self.last_activity_at = datetime.utcnow()

    def is_stale(self, timeout_seconds: int = 300) -> bool:
        """Check if session is stale (no activity for timeout_seconds)."""
        delta = datetime.utcnow() - self.last_activity_at
        return delta.total_seconds() > timeout_seconds
```

---

## 1.5 API Contract

### REST Endpoints

| Method | Path | Request | Response | Status Codes |
|--------|------|---------|----------|--------------|
| POST | `/api/v1/voice/session` | `CreateVoiceSessionCommand` | `VoiceSessionResponse` | 201, 400, 500 |
| DELETE | `/api/v1/voice/session/{session_id}` | - | `DeleteVoiceSessionResponse` | 200, 404, 500 |
| GET | `/api/v1/voice/health` | - | `HealthCheckResponse` | 200, 503 |

### WebSocket Channels

**Channel**: `/ws/voice` (port 8019)

| Message Type | Direction | Schema | Purpose |
|--------------|-----------|--------|---------|
| `SESSION_START` | Server → Client | `{"session_id": UUID}` | Confirm session started |
| `AUDIO_CHUNK` | Client → Server | `{"audio_bytes": "base64", "sample_rate": int}` | Send audio data |
| `TRANSCRIPT` | Server → Client | `{"text": str, "confidence": float, "is_final": bool}` | Send STT result |
| `RESPONSE_AUDIO` | Server → Client | `{"audio_bytes": "base64", "sample_rate": int, "is_interrupted": bool}` | Send TTS output |
| `INTERRUPT` | Client → Server | `{"interrupted": bool}` | Request interruption |
| `SESSION_END` | Server → Client | `{"session_id": UUID, "reason": str}` | Session terminated |

---

## 1.6 Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-VOICE-001 | Audio chunks MUST be resampled to 16kHz before STT | STTService resampling logic |
| BR-VOICE-002 | Silence MUST be filtered via VAD before STT | VADService probability threshold |
| BR-VOICE-003 | TTS chunks MUST be 500ms (12000 samples @ 24kHz) | TTSService chunking logic |
| BR-VOICE-004 | Sessions MUST auto-close after 5 minutes of inactivity | VoiceSessionEntity.is_stale() |
| BR-VOICE-005 | Interruption MUST terminate TTS within 200ms | Interrupt flag in TTS loop |
| BR-VOICE-006 | Max 5 concurrent sessions allowed | VoicePipelineUseCase limit |

---

## 1.7 Acceptance Criteria

- [ ] VoicePipelineUseCase orchestrates VAD → STT → LLM → TTS flow
- [ ] WebSocket supports simultaneous input/output (full duplex)
- [ ] Audio resampling works for any input sample rate
- [ ] VAD filters silence with <5% false positive rate
- [ ] STT transcribes with >90% accuracy on clear speech
- [ ] TTS streams audio in 500ms chunks
- [ ] Interruption terminates TTS within 200ms
- [ ] End-to-end latency <500ms (P95), <300ms (P50)
- [ ] Memory usage stays under 2GB after 1 hour
- [ ] 5 concurrent sessions work without degradation
- [ ] Sessions auto-close after 5 minutes of inactivity
- [ ] ExecuteAgentQueryUseCase integration works end-to-end
- [ ] Voice state UI updates emitted via `push_ui_message()`
- [ ] Voice nucleus widget displays with correct state (listening/processing/speaking)
- [ ] Interrupt button displays during TTS and sends INTERRUPT message
- [ ] Voice UI uses Shadow DOM for style isolation
- [ ] Voice nucleus uses platform-aware blur (16px desktop, 12px mobile)

---

## 1.8 Integration Points

| Component | Interface | Purpose |
|-----------|-----------|---------|
| **VADService** | `detect_speech(audio_bytes: bytes) -> float` | Return speech probability (0-1) |
| **STTService** | `transcribe(audio_bytes: bytes) -> str` | Transcribe audio to text |
| **C003 ExecuteAgentQueryUseCase** | `execute(command: ExecuteAgentQueryCommand) -> ExecuteAgentQueryResponse` | Process transcript through LLM |
| **TTSService** | `synthesize_stream(text: str) -> AsyncIterator[bytes]` | Stream audio chunks |
| **WebSocketManager** (C002) | `send_message(session_id, type, data)` | Send WebSocket messages |

---

## 1.9 Voice UI Widget Integration (from C007 Frontend Architecture)

### Voice State UI Updates

Voice pipeline MUST emit UI messages for voice state changes via `push_ui_message()`:

```python
from langgraph.graph.ui import push_ui_message

# Emit when voice state changes
push_ui_message(
    "voiceStatus",
    {
        "state": "listening",  # listening | processing | speaking
        "icon": "mic",         # mic | brain | speaker
        "pulse": True,         # Animate nucleus
    },
    message=None
)
```

### Voice Nucleus Widget (from C008 Organic UI)

Server-driven UI component for bio-inspired voice visual feedback:

| Property | Desktop | Mobile | Notes |
|----------|---------|--------|-------|
| Nucleus size | 160px | 72px | Adjusts per platform |
| Blur | 16px | 12px | Platform-aware |
| Max blobs | Unlimited | 6 | Mobile optimization |
| Colors | enzyme (#00D9FF) | enzyme (#00D9FF) | Cyan accent |

### Interrupt Button Pattern (Google Assistant Reference)

Server-driven UI button for voice interruption:

```python
# Emit interrupt button when speaking starts
push_ui_message(
    "interruptButton",
    {
        "label": "Stop",
        "action": "interrupt_voice",
        "variant": "destructive",  # Red outline
    },
    message=message
)
```

### Component Registration

```typescript
// src/agent/ui.tsx (colocated with graph.py)
export default {
  voiceStatus: VoiceNucleusWidget,
  interruptButton: ActionComponent,
};
```

---

## 1.10 DEPRECATED (2026-01-31)

**This spec is superseded by C010-voice-client.**

The internal voice pipeline (VAD → STT → LLM → TTS) described here has been replaced with external kyutai voice-server integration.

**Replacement**:
- **C010-voice-client** - External kyutai integration
- **`voice-gateway` spec** - VoiceGatewayService for kyutai routing
- **`conversational-state` spec** - ConversationStateManager for state tracking
- **`voice-stream-handling` spec** - TextStreamHandler for STT/TTS streaming

**Migration Path**:
- Internal `VoicePipelineUseCase` → External `VoiceGatewayService`
- Internal VAD/STT/TTS services → kyutai WebSocket connections
- Direct LLM calls → kyutai STT → AgentX → kyutai TTS flow
- Local session management → `ConversationStateManager`

**Related Specs**:
- `specs/vad-service/spec.md` - VAD filtering (deprecated, see C010)
- `specs/stt-service/spec.md` - Speech transcription (deprecated, see C010)
- `specs/tts-service/spec.md` - Text-to-speech synthesis (deprecated, see C010)
- `specs/voice-gateway/spec.md` - External kyutai integration (C010)
- `specs/conversational-state/spec.md` - Conversation state management (C010)
- `specs/voice-stream-handling/spec.md` - STT/TTS streaming (C010)
- C002 data contracts - WebSocket message types
- C003 agent pipeline - LLM integration
