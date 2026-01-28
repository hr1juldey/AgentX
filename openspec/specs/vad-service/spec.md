# Spec: vad-service

**File**: `specs/vad-service/spec.md`

**Generated**: 2026-01-28
**Change**: c004-voice-streaming

---

## 1.1 Purpose

Define Voice Activity Detection service using Silero VAD model to filter silence from audio input. The service processes audio chunks and returns speech probability scores, enabling the voice pipeline to skip STT processing for silence.

---

## 1.2 Scope

**In Scope**:
- Silero VAD model loading and initialization
- Audio resampling to 16kHz (required by Silero VAD)
- Speech probability detection (0.0-1.0 range)
- Processing latency <50ms per chunk
- Device selection (CPU/CUDA) based on availability

**Out of Scope**:
- Wake word detection (future feature)
- Speaker identification (future feature)
- Language detection (Silero VAD is language-agnostic)

---

## 1.3 Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-VAD-001 | Service MUST accept audio at any sample rate | Must |
| FR-VAD-002 | Service MUST resample audio to 16kHz for VAD processing | Must |
| FR-VAD-003 | Service MUST return speech probability (0.0-1.0) | Must |
| FR-VAD-004 | Service MUST process audio chunks in <50ms | Must |
| FR-VAD-005 | Service MUST load Silero VAD model on startup | Must |
| FR-VAD-006 | Service MUST support CPU and CUDA device selection | Should |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-VAD-001 | Speech probability accuracy MUST be >95% | Must |
| NFR-VAD-002 | False positive rate MUST be <5% (silence detected as speech) | Must |
| NFR-VAD-003 | Memory footprint MUST be <100MB | Should |
| NFR-VAD-004 | Service MUST be thread-safe for concurrent access | Must |

---

## 1.4 Data Model

```python
# File: infrastructure/external/vad_service.py
from dataclasses import dataclass
from typing import Optional
import torch


@dataclass
class VADResult:
    """Result from VAD processing."""

    speech_probability: float
    """Probability of speech presence (0.0-1.0)."""

    is_speech: bool
    """Whether speech is detected (based on threshold)."""

    processing_time_ms: float
    """Time taken to process the audio chunk."""

    sample_rate: int
    """Sample rate of the processed audio."""

    chunk_size_ms: int
    """Size of the audio chunk in milliseconds."""


class VADService:
    """Voice Activity Detection service using Silero VAD.

    Silero VAD model requirements:
    - Input: 16kHz sample rate, mono audio
    - Output: Speech probability (0.0-1.0)
    - Latency: <50ms
    - Model size: ~8MB

    Reference: research/08_tts_stt_integration.md
    """

    VAD_SAMPLE_RATE = 16000
    """Required sample rate for Silero VAD."""

    DEFAULT_THRESHOLD = 0.5
    """Default speech probability threshold."""

    DEFAULT_CHUNK_MS = 500
    """Default chunk size in milliseconds."""

    def __init__(self, threshold: float = DEFAULT_THRESHOLD, device: Optional[str] = None):
        """Initialize VAD service.

        Args:
            threshold: Speech probability threshold (0.0-1.0). Default: 0.5
            device: Torch device ("cpu" or "cuda"). Default: auto-detect
        """
        self._threshold = threshold
        self._torch_device = self._get_device(device)
        self._vad_model = None  # Loaded in _load_model()

        self._load_model()

    def detect_speech(self, audio_bytes: bytes, sample_rate: int) -> VADResult:
        """Detect speech in audio chunk.

        Args:
            audio_bytes: WAV audio data (any sample rate)
            sample_rate: Original sample rate of audio

        Returns:
            VADResult with speech probability and classification
        """

    async def adetect_speech(self, audio_bytes: bytes, sample_rate: int) -> VADResult:
        """Async version of detect_speech."""

    def _load_model(self) -> None:
        """Load Silero VAD model from torch.hub."""

    @staticmethod
    def _get_device(device: Optional[str]) -> torch.device:
        """Get torch device, auto-detect if not specified."""
```

---

## 1.5 API Contract

### Internal Interface

| Method | Input | Output | Description |
|--------|-------|--------|-------------|
| `detect_speech()` | `audio_bytes: bytes, sample_rate: int` | `VADResult` | Detect speech in audio chunk |
| `adetect_speech()` | `audio_bytes: bytes, sample_rate: int` | `VADResult` | Async version of detect_speech |

### Usage Example

```python
# File: application/use_cases/voice_pipeline_use_case.py
from infrastructure.external.vad_service import VADService, VADResult

vad_service = VADService(threshold=0.5)

async def process_audio_chunk(audio_bytes: bytes, sample_rate: int) -> None:
    # Check for speech
    vad_result = await vad_service.adetect_speech(audio_bytes, sample_rate)

    if vad_result.is_speech:
        # Forward to STT
        transcript = await stt_service.transcribe(audio_bytes)
    else:
        # Skip STT processing (silence)
        logger.debug(f"Silence detected (prob: {vad_result.speech_probability:.2f})")
```

---

## 1.6 Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-VAD-001 | Audio MUST be resampled to 16kHz before VAD processing | VADService._resample_audio() |
| BR-VAD-002 | Speech probability threshold default is 0.5 | VADService.DEFAULT_THRESHOLD |
| BR-VAD-003 | Stereo audio MUST be converted to mono | VADService._to_mono() |
| BR-VAD-004 | Processing MUST complete in <50ms | VADResult.processing_time_ms |

---

## 1.7 Acceptance Criteria

- [ ] VADService loads Silero VAD model on startup
- [ ] VADService accepts audio at any sample rate
- [ ] Audio is resampled to 16kHz before processing
- [ ] Stereo audio is converted to mono
- [ ] Speech probability returned in 0.0-1.0 range
- [ ] is_speech boolean based on threshold (default 0.5)
- [ ] Processing latency <50ms per chunk
- [ ] Speech probability accuracy >95%
- [ ] False positive rate <5%
- [ ] Auto-detects CUDA if available
- [ ] Thread-safe for concurrent access
- [ ] Memory footprint <100MB

---

## 1.8 Configuration

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `threshold` | 0.5 | 0.0-1.0 | Speech probability threshold |
| `chunk_ms` | 500 | 100-2000 | Audio chunk size in milliseconds |
| `device` | auto | cpu/cuda | Torch device for inference |

---

**Related Specs**:
- `specs/voice-pipeline/spec.md` - Voice pipeline orchestration
- `specs/stt-service/spec.md` - Speech transcription (uses VAD output)
- research/08_tts_stt_integration.md - VAD patterns and best practices
