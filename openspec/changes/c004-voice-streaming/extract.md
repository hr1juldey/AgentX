# Extract Artifact: c004-voice-streaming

**Generated**: 2026-01-28
**Change**: c004-voice-streaming
**Schema**: spec-factory v1

---

## 1. Pattern Catalog

### 1.1 Architectural Patterns

| Pattern | Source | Description | Apply? |
|---------|--------|-------------|--------|
| **WebSocket Bidirectional Streaming** | R011 + research | Full duplex audio communication with separate input/output tasks | ✅ |
| **Three-Stage Voice Pipeline** | research:08_tts_stt_integration | VAD → STT/LLM → TTS with streaming between stages | ✅ |
| **Queue-Based Decoupling** | R011 + LLD | asyncio.Queue between WebSocket and processing workers | ✅ |
| **Interruptible Pipeline** | research:08_tts_stt_integration | VAD monitoring during TTS for early termination | ✅ |
| **Streaming Chunk Pattern** | research:08_tts_stt_integration | 500ms audio chunks for low latency (<300ms target) | ✅ |
| **Clean Architecture** | mimicus | Voice services in infrastructure layer, use cases for orchestration | ✅ |
| **Memory Management** | research:08_tts_stt_integration | Periodic TTS model reload to prevent 32GB+ growth | ✅ |

### 1.2 Code Structure Patterns

| Pattern | Example | Apply? |
|---------|---------|--------|
| **Separate VAD Service** | `class VADService:` | ✅ |
| **Separate STT Service** | `class STTService:` | ✅ |
| **Separate TTS Service** | `class TTSService:` | ✅ |
| **WebSocket Input/Output Tasks** | `async def input_task():`, `async def output_task():` | ✅ |
| **Audio Resampling** | `Resample(sr, 16000)` for STT input | ✅ |
| **Interrupt Flag Pattern** | `self.interrupted = False` checked in loops | ✅ |
| **Full Duplex WebSocket** | `websocket.accept()` with concurrent tasks | ✅ |

### 1.3 Naming Patterns (to Avoid from R011)

| R011 Name | Why Avoid | Alternative |
|-----------|-----------|-------------|
| `stt_service.py` with combined VAD+STT | Tight coupling, hard to test VAD separately | Split: `vad_service.py`, `stt_service.py` |
| `tts_service.py` without memory management | Memory leak grows to 32GB+ | Add reload strategy |
| Single WebSocket task | Can't handle bidirectional streaming | Use `input_task` + `output_task` pattern |
| Blocking TTS generation | Blocks interruption, poor UX | Stream TTS output |
| Large audio chunks (>1s) | High latency, slow interruption | Use 500ms chunks (0.5s @ 24kHz) |

---

## 2. Specification Drafts

### 2.1 Draft: voice-pipeline Spec

**Purpose**: Define the streaming voice pipeline architecture with VAD, STT, LLM, and TTS integration.

**Scope**:
- In scope: Audio input processing, VAD filtering, STT transcription, LLM integration, TTS synthesis, WebSocket streaming
- Out of scope: Voice wake word detection (separate feature), speaker recognition (future)

**Locked from LLD**:

```python
# infrastructure_adapters.md:716-828 (WebSocketManager - LOCKED)
class WebSocketManager:
    """Manages WebSocket connections for streaming UI updates."""

    def __init__(self):
        self._connections: Dict[UUID, WebSocket] = {}
        self._queues: Dict[UUID, asyncio.Queue] = {}

    async def connect(self, session_id: UUID, websocket: WebSocket) -> None
    def disconnect(self, session_id: UUID) -> None
    async def send_message(self, session_id: UUID, message_type: WebSocketMessageType, data: Dict[str, Any]) -> None
    async def broadcast(self, message_type: WebSocketMessageType, data: Dict[str, Any]) -> None
    async def stream_tokens(self, session_id: UUID, token_generator: Any) -> None
    async def send_ui_descriptor(self, session_id: UUID, descriptor: Dict[str, Any], action: str = "create") -> None
    def get_queue(self, session_id: UUID) -> asyncio.Queue
    async def process_queue(self, session_id: UUID) -> None
```

**Requirements**:
1. **FR-VOICE-001**: System MUST accept audio input at any sample rate and resample to 16kHz for STT
2. **FR-VOICE-002**: System MUST use VAD to filter silence before STT processing
3. **FR-VOICE-003**: System MUST stream audio output in 500ms chunks for <300ms latency
4. **FR-VOICE-004**: System MUST support full-duplex WebSocket (simultaneous input/output)
5. **FR-VOICE-005**: System MUST monitor VAD during TTS for interruption handling
6. **FR-VOICE-006**: System MUST reload TTS model periodically to prevent memory leaks
7. **FR-VOICE-007**: System MUST integrate with C003 agent pipeline for LLM processing
8. **FR-VOICE-008**: System MUST use separate tasks for input and output WebSocket streams

**Acceptance Criteria**:
- [ ] VAD filters silence with <50ms latency
- [ ] STT transcribes audio at 16kHz sample rate
- [ ] TTS generates audio at 24kHz or 48kHz sample rate
- [ ] WebSocket supports simultaneous bidirectional streaming
- [ ] Interruption terminates TTS within 200ms
- [ ] Memory usage stays under 2GB after 1 hour of operation
- [ ] End-to-end latency <500ms (target: 300ms)
- [ ] Agent pipeline integration via ExecuteAgentQueryUseCase

---

### 2.2 Draft: vad-service Spec

**Purpose**: Define Voice Activity Detection service using Silero VAD for silence filtering.

**Scope**:
- In scope: Silero VAD integration, speech probability detection, audio chunking
- Out of scope: Wake word detection, speaker identification

**Locked from Research**:

```python
# research:08_tts_stt_integration.md
from silero_vad import VADIterator, load_silero_vad

vad_model = load_silero_vad()
speech_prob = vad_model(torch_tensor(audio_np).float().to(_torch_device), sr=16000).item()
```

**Requirements**:
1. **FR-VAD-001**: Service MUST accept audio at any sample rate
2. **FR-VAD-002**: Service MUST resample to 16kHz for VAD processing
3. **FR-VAD-003**: Service MUST return speech probability (0.0-1.0)
4. **FR-VAD-004**: Service MUST process audio in <50ms

**Acceptance Criteria**:
- [ ] VAD model loaded on startup
- [ ] Speech probability accuracy >95%
- [ ] Processing latency <50ms per chunk
- [ ] Resampling works for any input sample rate

---

### 2.3 Draft: stt-service Spec

**Purpose**: Define Speech-to-Text service using Kyutai STT 2.6B for transcription.

**Scope**:
- In scope: Kyutai STT 2.6B integration, audio transcription, streaming support
- Out of scope: Real-time streaming transcription (future), multi-language support (future: English only)

**Locked from Research**:

```python
# research:08_tts_stt_integration.md
from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq

stt_model = AutoModelForSpeechSeq2Seq.from_pretrained("kyutai/stt-2.6b-en")
stt_processor = AutoProcessor.from_pretrained("kyutai/stt-2.6b-en")
```

**Requirements**:
1. **FR-STT-001**: Service MUST accept audio at 16kHz sample rate
2. **FR-STT-002**: Service MUST resample input audio to 16kHz if needed
3. **FR-STT-003**: Service MUST convert stereo to mono
4. **FR-STT-004**: Service MUST return transcribed text

**Acceptance Criteria**:
- [ ] STT model loaded on startup
- [ ] Transcription accuracy >90% on clear speech
- [ ] Resampling from any input sample rate
- [ ] Stereo to mono conversion works correctly

---

### 2.4 Draft: tts-service Spec

**Purpose**: Define Text-to-Speech service using Pocket TTS for speech synthesis.

**Scope**:
- In scope: Pocket TTS integration, text-to-audio synthesis, memory management
- Out of scope: Voice cloning, emotion control (future)

**Locked from Research**:

```python
# research:08_tts_stt_integration.md
from transformers import AutoProcessor, VitsModel

tts_model = VitsModel.from_pretrained("kyutai/pocket-tts")
tts_processor = AutoProcessor.from_pretrained("kyutai/pocket-tts")

audio = tts_model.generate_audio(text, speaker=5)
```

**Requirements**:
1. **FR-TTS-001**: Service MUST synthesize audio at 24kHz or 48kHz sample rate
2. **FR-TTS-002**: Service MUST stream output in 500ms chunks
3. **FR-TTS-003**: Service MUST reload model every N generations to prevent memory leaks
4. **FR-TTS-004**: Service MUST support interruption via flag check

**Acceptance Criteria**:
- [ ] TTS model loaded on startup
- [ ] Audio output at 24kHz sample rate
- [ ] Streaming chunks of 500ms (12000 samples @ 24kHz)
- [ ] Model reload prevents memory growth
- [ ] Interruption terminates generation within 100ms

---

## 3. API Contracts

### 3.1 REST Endpoints

| Method | Path | Request | Response |
|--------|------|---------|----------|
| POST | `/api/v1/voice/session` | `CreateVoiceSessionCommand` | `VoiceSessionResponse` |
| DELETE | `/api/v1/voice/session/{session_id}` | - | `DeleteVoiceSessionResponse` |
| GET | `/api/v1/voice/health` | - | `HealthCheckResponse` |

### 3.2 WebSocket Channels

| Channel | Message Type | Schema |
|---------|--------------|--------|
| `/ws/voice` | `AUDIO_CHUNK` | `{"audio_bytes": "base64", "sample_rate": int}` |
| `/ws/voice` | `TRANSCRIPT` | `{"text": str, "confidence": float}` |
| `/ws/voice` | `RESPONSE_AUDIO` | `{"audio_bytes": "base64", "sample_rate": int}` |
| `/ws/voice` | `INTERRUPT` | `{"interrupted": bool}` |
| `/ws/voice` | `SESSION_START` | `{"session_id": UUID}` |
| `/ws/voice` | `SESSION_END` | `{"session_id": UUID, "reason": str}` |

### 3.3 Port Assignments

| Service | Port | Purpose |
|---------|------|---------|
| Voice API | 8018 | REST endpoints for session management |
| Voice WebSocket | 8019 | Bidirectional audio streaming |
| Voice Health | 8020 | Health check endpoint |

**Note**: Ports 8015-8017 reserved for C003-agent-pipeline. Using 8018-8020 for voice services.

---

## 4. Data Model Mappings

### 4.1 Pydantic → Zod Mappings

| Pydantic Model | Zod Type | Notes |
|----------------|----------|-------|
| `CreateVoiceSessionCommand` | `CreateVoiceSessionCommandSchema` | Session initialization |
| `VoiceSessionResponse` | `VoiceSessionResponseSchema` | Session created confirmation |
| `AudioChunkMessage` | `AudioChunkMessageSchema` | Binary audio data |
| `TranscriptMessage` | `TranscriptMessageSchema` | STT output |
| `ResponseAudioMessage` | `ResponseAudioMessageSchema` | TTS output |

### 4.2 Shared Types

```python
# Backend (Pydantic v2)
# File: application/dtos/voice_dtos.py
from pydantic import BaseModel, Field
from uuid import UUID
from typing import Literal

class AudioChunkMessage(BaseModel):
    """Audio chunk sent from client to server."""
    audio_bytes: bytes = Field(..., description="Base64-encoded audio data")
    sample_rate: int = Field(..., ge=8000, le=48000, description="Audio sample rate")
    format: Literal["wav", "pcm"] = Field(default="wav", description="Audio format")

class TranscriptMessage(BaseModel):
    """Transcription result sent from server to client."""
    text: str = Field(..., min_length=1, description="Transcribed text")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Transcription confidence")
    is_final: bool = Field(default=False, description="Whether this is final transcription")

class ResponseAudioMessage(BaseModel):
    """Audio response sent from server to client."""
    audio_bytes: bytes = Field(..., description="Base64-encoded audio data")
    sample_rate: int = Field(default=24000, description="Audio sample rate (24kHz or 48kHz)")
    format: Literal["wav"] = Field(default="wav", description="Audio format")
    is_interrupted: bool = Field(default=False, description="Whether this response was interrupted")

class InterruptMessage(BaseModel):
    """Interruption signal from client to server."""
    interrupted: bool = Field(default=True, description="Signal to interrupt current TTS")
```

```typescript
// Frontend (Zod)
// File: frontend/types/voice.ts
import { z } from "zod";

export const AudioChunkMessageSchema = z.object({
  audio_bytes: z.string(), // Base64 encoded
  sample_rate: z.number().min(8000).max(48000),
  format: z.enum(["wav", "pcm"]).default("wav"),
});

export const TranscriptMessageSchema = z.object({
  text: z.string().min(1),
  confidence: z.number().min(0).max(1),
  is_final: z.boolean().default(false),
});

export const ResponseAudioMessageSchema = z.object({
  audio_bytes: z.string(), // Base64 encoded
  sample_rate: z.number().default(24000),
  format: z.literal("wav"),
  is_interrupted: z.boolean().default(false),
});

export const InterruptMessageSchema = z.object({
  interrupted: z.boolean().default(true),
});
```

### 4.3 Audio Format Specifications

| Purpose | Sample Rate | Format | Chunk Size |
|---------|-------------|--------|------------|
| **STT Input** | 16kHz | WAV (mono) | Variable |
| **TTS Output** | 24kHz or 48kHz | WAV (mono) | 500ms (12000 samples @ 24kHz) |
| **VAD Processing** | 16kHz | Tensor | Any |
| **Client Input** | Any | WAV | Recommended 500ms |
| **Client Output** | 24kHz | WAV | 500ms chunks |

---

## 5. Dependencies on Other Specs

| Spec | Dependency Type | Rationale |
|------|-----------------|-----------|
| **C001-folder-structure** | Structural | Provides Clean Architecture layers for voice services |
| **C002-data-contracts** | Contract | Defines WebSocket message types (AUDIO_CHUNK, TRANSCRIPT, etc.) |
| **C003-agent-pipeline** | Functional | Provides ExecuteAgentQueryUseCase for LLM integration |
| **infrastructure_adapters LLD** | Locked | WebSocketManager class definition for streaming |
| **08_tts_stt_integration research** | Reference | Voice pipeline patterns, anti-patterns, best practices |

---

**Next Artifact**: validate.md
