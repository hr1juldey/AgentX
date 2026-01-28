# Specs Artifact: c004-voice-streaming

**Generated**: 2026-01-28
**Change**: c004-voice-streaming
**Schema**: spec-factory v1

---

## Spec Structure

This artifact generates domain-specific specification files in `specs/{domain}/spec.md`.

---

## 1. Spec: voice-pipeline

**File**: `specs/voice-pipeline/spec.md`

### 1.1 Purpose

Define the streaming voice pipeline that orchestrates VAD filtering, STT transcription, LLM processing via C003 agent pipeline, and TTS synthesis. The pipeline supports full-duplex WebSocket communication with interruption handling.

### 1.2 Key Requirements

- **FR-VOICE-001**: Pipeline MUST accept audio input at any sample rate and resample to 16kHz for STT
- **FR-VOICE-002**: Pipeline MUST use VAD to filter silence before STT processing
- **FR-VOICE-003**: Pipeline MUST stream TTS output in 500ms chunks
- **FR-VOICE-004**: Pipeline MUST support full-duplex WebSocket (simultaneous input/output)
- **FR-VOICE-005**: Pipeline MUST monitor VAD during TTS for interruption handling

### 1.3 Locked from LLD

```python
# infrastructure_adapters.md:716-828 (WebSocketManager - LOCKED)
class WebSocketManager:
    async def send_message(self, session_id: UUID, message_type: WebSocketMessageType, data: Dict[str, Any]) -> None
    async def stream_tokens(self, session_id: UUID, token_generator: Any) -> None
    def get_queue(self, session_id: UUID) -> asyncio.Queue
```

### 1.4 API Contract

| Method | Path | Request | Response |
|--------|------|---------|----------|
| POST | `/api/v1/voice/session` | `CreateVoiceSessionCommand` | `VoiceSessionResponse` |
| DELETE | `/api/v1/voice/session/{session_id}` | - | `DeleteVoiceSessionResponse` |
| WebSocket | `/ws/voice` | `AUDIO_CHUNK`, `INTERRUPT` | `TRANSCRIPT`, `RESPONSE_AUDIO` |

---

## 2. Spec: vad-service

**File**: `specs/vad-service/spec.md`

### 2.1 Purpose

Define Voice Activity Detection service using Silero VAD model to filter silence from audio input. The service processes audio chunks and returns speech probability scores.

### 2.2 Key Requirements

- **FR-VAD-001**: Service MUST accept audio at any sample rate
- **FR-VAD-002**: Service MUST resample audio to 16kHz for VAD processing
- **FR-VAD-003**: Service MUST return speech probability (0.0-1.0)
- **FR-VAD-004**: Service MUST process audio chunks in <50ms

### 2.3 Locked from Research

```python
# research:08_tts_stt_integration.md
from silero_vad import VADIterator, load_silero_vad

vad_model = load_silero_vad()
speech_prob = vad_model(torch_tensor(audio_np).float().to(_torch_device), sr=16000).item()
```

---

## 3. Spec: stt-service

**File**: `specs/stt-service/spec.md`

### 3.1 Purpose

Define Speech-to-Text service using Kyutai STT 2.6B model for transcribing English audio. The service accepts audio at any sample rate, preprocesses it, and returns transcribed text.

### 3.2 Key Requirements

- **FR-STT-001**: Service MUST accept audio at any sample rate
- **FR-STT-002**: Service MUST resample audio to 16kHz for STT model
- **FR-STT-003**: Service MUST convert stereo audio to mono
- **FR-STT-004**: Service MUST return transcribed text

### 3.3 Model Specifications

| Property | Value |
|----------|-------|
| **Model** | Kyutai STT 2.6B-en |
| **Parameters** | 2.6B |
| **Sample Rate** | 16kHz |
| **Language** | English only |

---

## 4. Spec: tts-service

**File**: `specs/tts-service/spec.md`

### 4.1 Purpose

Define Text-to-Speech service using Pocket TTS (kyutai/pocket-tts) for synthesizing speech from text. The service generates audio at 24kHz sample rate, streams output in 500ms chunks, and includes memory management.

### 4.2 Key Requirements

- **FR-TTS-001**: Service MUST synthesize audio at 24kHz sample rate
- **FR-TTS-002**: Service MUST stream output in 500ms chunks
- **FR-TTS-003**: Service MUST support interruption via flag check
- **FR-TTS-004**: Service MUST reload model every N generations to prevent memory leaks

### 4.3 Model Specifications

| Property | Value |
|----------|-------|
| **Model** | kyutai/pocket-tts |
| **Parameters** | 100M |
| **Sample Rate** | 24kHz or 48kHz |
| **Speakers** | 6 (English) |

---

## 5. Cross-Domain Contracts

### 5.1 Shared Types

**VoiceSessionState** (used by voice-pipeline):
```python
class VoiceSessionState(str, Enum):
    CREATED = "created"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    CLOSED = "closed"
```

### 5.2 Integration Points

| Domain A | Domain B | Interface |
|----------|----------|-----------|
| **voice-pipeline** | **vad-service** | VADService.detect_speech() → VADResult |
| **voice-pipeline** | **stt-service** | STTService.transcribe() → STTResult |
| **voice-pipeline** | **tts-service** | TTSService.astream_synthesize() → AsyncIterator[TTSChunk] |
| **voice-pipeline** | **C003-agent-pipeline** | ExecuteAgentQueryUseCase.execute() → ExecuteAgentQueryResponse |
| **voice-pipeline** | **C002-data-contracts** | WebSocketManager.send_message() |

### 5.3 Data Flow

```
Client Audio → WebSocket (port 8019)
    ↓
VoicePipelineUseCase
    ↓
VADService.detect_speech() → Speech Probability
    ↓ (if speech)
STTService.transcribe() → Transcript Text
    ↓
ExecuteAgentQueryUseCase (C003) → LLM Response
    ↓
TTSService.astream_synthesize() → Audio Chunks
    ↓
WebSocket → Client Audio
```

---

## 6. Pydantic → Zod Type Mappings

### 6.1 Shared DTOs

**Backend (Pydantic v2)**:
```python
class AudioChunkMessage(BaseModel):
    audio_bytes: bytes
    sample_rate: int = Field(..., ge=8000, le=48000)
    format: Literal["wav", "pcm"] = Field(default="wav")

class TranscriptMessage(BaseModel):
    text: str = Field(..., min_length=1)
    confidence: float = Field(..., ge=0.0, le=1.0)
    is_final: bool = Field(default=False)

class ResponseAudioMessage(BaseModel):
    audio_bytes: bytes
    sample_rate: int = Field(default=24000)
    format: Literal["wav"] = Field(default="wav")
    is_interrupted: bool = Field(default=False)
```

**Frontend (Zod)**:
```typescript
export const AudioChunkMessageSchema = z.object({
  audio_bytes: z.string(),
  sample_rate: z.number().min(8000).max(48000),
  format: z.enum(["wav", "pcm"]).default("wav"),
});

export const TranscriptMessageSchema = z.object({
  text: z.string().min(1),
  confidence: z.number().min(0).max(1),
  is_final: z.boolean().default(false),
});

export const ResponseAudioMessageSchema = z.object({
  audio_bytes: z.string(),
  sample_rate: z.number().default(24000),
  format: z.literal("wav"),
  is_interrupted: z.boolean().default(false),
});
```

---

**Next Artifact**: design.md
