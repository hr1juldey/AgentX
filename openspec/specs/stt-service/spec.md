# Spec: stt-service

**File**: `specs/stt-service/spec.md`

**Generated**: 2026-01-28
**Change**: c004-voice-streaming

---

## 1.1 Purpose

Define Speech-to-Text service using Kyutai STT 2.6B model for transcribing English audio. The service accepts audio at any sample rate, preprocesses it (resample to 16kHz, convert to mono), and returns transcribed text.

---

## 1.2 Scope

**In Scope**:
- Kyutai STT 2.6B model loading and initialization
- Audio preprocessing (resampling, mono conversion)
- English speech transcription
- Streaming transcription support (future enhancement)
- Device selection (CPU/CUDA) based on availability

**Out of Scope**:
- Multi-language support (Kyutai STT 2.6B is English-only)
- Real-time streaming transcription (future: STT-STREAMING)
- Speaker diarization (future feature)
- Punctuation/capitalization (LLM post-processing)

---

## 1.3 Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-STT-001 | Service MUST accept audio at any sample rate | Must |
| FR-STT-002 | Service MUST resample audio to 16kHz for STT model | Must |
| FR-STT-003 | Service MUST convert stereo audio to mono | Must |
| FR-STT-004 | Service MUST return transcribed text | Must |
| FR-STT-005 | Service MUST load Kyutai STT 2.6B model on startup | Must |
| FR-STT-006 | Service MUST support CPU and CUDA device selection | Should |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-STT-001 | Word accuracy MUST be >90% on clear speech | Must |
| NFR-STT-002 | Processing latency MUST be <200ms per chunk | Must |
| NFR-STT-003 | Memory footprint MUST be <5GB | Should |
| NFR-STT-004 | Service MUST be thread-safe for concurrent access | Must |

---

## 1.4 Data Model

```python
# File: infrastructure/external/stt_service.py
from dataclasses import dataclass
from typing import Optional
import torch


@dataclass
class STTResult:
    """Result from STT processing."""

    text: str
    """Transcribed text."""

    confidence: float
    """Transcription confidence score (0.0-1.0)."""

    processing_time_ms: float
    """Time taken to transcribe the audio."""

    input_sample_rate: int
    """Original sample rate of input audio."""

    input_duration_ms: float
    """Duration of input audio in milliseconds."""


class STTService:
    """Speech-to-Text service using Kyutai STT 2.6B.

    Kyutai STT 2.6B model requirements:
    - Input: 16kHz sample rate, mono audio
    - Output: English text transcription
    - Latency: <200ms
    - Model size: ~5GB
    - Parameters: 2.6B

    Reference: research/08_tts_stt_integration.md
    """

    STT_SAMPLE_RATE = 16000
    """Required sample rate for Kyutai STT 2.6B."""

    MODEL_NAME = "kyutai/stt-2.6b-en"
    """HuggingFace model identifier."""

    def __init__(self, device: Optional[str] = None):
        """Initialize STT service.

        Args:
            device: Torch device ("cpu" or "cuda"). Default: auto-detect
        """
        self._torch_device = self._get_device(device)
        self._stt_model = None
        self._stt_processor = None

        self._load_model()

    def transcribe(self, audio_bytes: bytes, sample_rate: int) -> STTResult:
        """Transcribe audio to text.

        Args:
            audio_bytes: WAV audio data (any sample rate)
            sample_rate: Original sample rate of audio

        Returns:
            STTResult with transcribed text and metadata
        """

    async def atranscribe(self, audio_bytes: bytes, sample_rate: int) -> STTResult:
        """Async version of transcribe."""

    def _load_model(self) -> None:
        """Load Kyutai STT 2.6B model from HuggingFace."""

    @staticmethod
    def _get_device(device: Optional[str]) -> torch.device:
        """Get torch device, auto-detect if not specified."""

    def _resample_audio(self, audio_tensor: torch.Tensor, original_sr: int) -> torch.Tensor:
        """Resample audio to 16kHz."""

    def _to_mono(self, audio_tensor: torch.Tensor) -> torch.Tensor:
        """Convert stereo audio to mono."""
```

---

## 1.5 API Contract

### Internal Interface

| Method | Input | Output | Description |
|--------|-------|--------|-------------|
| `transcribe()` | `audio_bytes: bytes, sample_rate: int` | `STTResult` | Transcribe audio to text |
| `atranscribe()` | `audio_bytes: bytes, sample_rate: int` | `STTResult` | Async version of transcribe |

### Usage Example

```python
# File: application/use_cases/voice_pipeline_use_case.py
from infrastructure.external.stt_service import STTService, STTResult
from infrastructure.external.vad_service import VADService

vad_service = VADService(threshold=0.5)
stt_service = STTService()

async def process_audio_chunk(audio_bytes: bytes, sample_rate: int) -> Optional[str]:
    # First, check for speech
    vad_result = await vad_service.adetect_speech(audio_bytes, sample_rate)

    if not vad_result.is_speech:
        return None  # Skip silence

    # Transcribe speech
    stt_result = await stt_service.atranscribe(audio_bytes, sample_rate)

    logger.info(f"Transcribed: {stt_result.text} (confidence: {stt_result.confidence:.2f})")

    return stt_result.text
```

---

## 1.6 Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-STT-001 | Audio MUST be resampled to 16kHz before STT processing | STTService._resample_audio() |
| BR-STT-002 | Stereo audio MUST be converted to mono | STTService._to_mono() |
| BR-STT-003 | Only English transcription is supported | MODEL_NAME = "kyutai/stt-2.6b-en" |
| BR-STT-004 | Processing MUST complete in <200ms for 500ms chunk | STTResult.processing_time_ms |

---

## 1.7 Acceptance Criteria

- [ ] STTService loads Kyutai STT 2.6B model on startup
- [ ] STTService accepts audio at any sample rate
- [ ] Audio is resampled to 16kHz before processing
- [ ] Stereo audio is converted to mono
- [ ] Transcribed text is returned
- [ ] Confidence score is included (0.0-1.0)
- [ ] Processing latency <200ms per 500ms chunk
- [ ] Word accuracy >90% on clear speech
- [ ] Auto-detects CUDA if available
- [ ] Thread-safe for concurrent access
- [ ] Memory footprint <5GB
- [ ] Empty audio returns empty string (not error)

---

## 1.8 Configuration

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `device` | auto | cpu/cuda | Torch device for inference |
| `chunk_ms` | 500 | 100-2000 | Audio chunk size in milliseconds |

---

## 1.9 Model Specifications

| Property | Value | Source |
|----------|-------|--------|
| **Model Name** | Kyutai STT 2.6B-en | HuggingFace |
| **Parameters** | 2.6B | Model spec |
| **Sample Rate** | 16kHz | Model requirement |
| **Channels** | Mono (1) | Model requirement |
| **Language** | English | Model limitation |
| **Model Size** | ~5GB | Disk space |
| **Memory** | ~5GB | Runtime (CPU) |

---

## 1.10 DEPRECATED (2026-01-31)

**This spec is superseded by C010-voice-client.**

The internal STT service described here has been replaced with external kyutai STT integration via `VoiceGatewayService`.

**Replacement**:
- **C010-voice-client** - External kyutai STT WebSocket integration
- **`voice-gateway` spec** - VoiceGatewayService for kyutai routing
- **`voice-stream-handling` spec** - TextStreamHandler for STT buffering

**Migration Path**:
- Internal `STTService` → External `VoiceGatewayService` with kyutai STT WebSocket
- Direct model loading → WebSocket connection to kyutai server
- Local audio preprocessing → Handled by kyutai service

**Related Specs**:
- `specs/voice-pipeline/spec.md` - Voice pipeline orchestration
- `specs/vad-service/spec.md` - VAD filtering (pre-processing for STT)
- `specs/voice-gateway/spec.md` - External kyutai integration (C010)
- `specs/voice-stream-handling/spec.md` - STT buffering (C010)
- research/08_tts_stt_integration.md - STT patterns and best practices
