# Spec: tts-service

**File**: `specs/tts-service/spec.md`

**Generated**: 2026-01-28
**Change**: c004-voice-streaming

---

## 1.1 Purpose

Define Text-to-Speech service using Pocket TTS (kyutai/pocket-tts) for synthesizing speech from text. The service generates audio at 24kHz sample rate, streams output in 500ms chunks, and includes memory management to prevent unbounded growth.

---

## 1.2 Scope

**In Scope**:
- Pocket TTS model loading and initialization
- Text-to-audio synthesis at 24kHz sample rate
- Streaming output in 500ms chunks
- Interruption support (early termination on flag)
- Memory management (periodic model reload)
- Device selection (CPU/CUDA) based on availability

**Out of Scope**:
- Voice cloning (future feature)
- Emotion control (future feature)
- Multi-speaker support (Pocket TTS has 6 speakers, use default)
- SSML support (future enhancement)

---

## 1.3 Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-TTS-001 | Service MUST synthesize audio at 24kHz sample rate | Must |
| FR-TTS-002 | Service MUST stream output in 500ms chunks | Must |
| FR-TTS-003 | Service MUST support interruption via flag check | Must |
| FR-TTS-004 | Service MUST reload model every N generations to prevent memory leaks | Must |
| FR-TTS-005 | Service MUST load Pocket TTS model on startup | Must |
| FR-TTS-006 | Service MUST support CPU and CUDA device selection | Should |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-TTS-001 | Synthesis latency MUST be <100ms for first chunk | Must |
| NFR-TTS-002 | Interruption latency MUST be <200ms | Must |
| NFR-TTS-003 | Memory usage MUST stay under 2GB after 1 hour | Must |
| NFR-TTS-004 | Service MUST be thread-safe for concurrent access | Must |

---

## 1.4 Data Model

```python
# File: infrastructure/external/tts_service.py
from dataclasses import dataclass
from typing import AsyncIterator, Optional
import torch


@dataclass
class TTSChunk:
    """Audio chunk from TTS synthesis."""

    audio_bytes: bytes
    """WAV audio data (24kHz, mono)."""

    chunk_index: int
    """Chunk sequence number (0-based)."""

    is_final: bool
    """Whether this is the final chunk."""

    sample_rate: int = 24000
    """Sample rate (24kHz for Pocket TTS)."""

    duration_ms: float = 500.0
    """Chunk duration in milliseconds."""


class TTSService:
    """Text-to-Speech service using Pocket TTS.

    Pocket TTS model specifications:
    - Input: Text string
    - Output: 24kHz or 48kHz audio, mono
    - Parameters: 100M
    - Latency: <200ms
    - Model size: ~400MB
    - Speakers: 6 (use speaker 5 by default)

    Memory Management:
    - Reload model every 100 generations to prevent memory leaks
    - Observed growth: 32GB+ without reload (R011 prototype)

    Reference: research/08_tts_stt_integration.md
    """

    TTS_SAMPLE_RATE = 24000
    """Output sample rate for Pocket TTS."""

    MODEL_NAME = "kyutai/pocket-tts"
    """HuggingFace model identifier."""

    DEFAULT_SPEAKER = 5
    """Default speaker ID (en_5)."""

    CHUNK_SAMPLES = 12000
    """Samples per 500ms chunk at 24kHz (24000 * 0.5)."""

    RELOAD_INTERVAL = 100
    """Model reload interval (number of synthesize calls)."""

    def __init__(self, speaker: int = DEFAULT_SPEAKER, reload_interval: int = RELOAD_INTERVAL, device: Optional[str] = None):
        """Initialize TTS service.

        Args:
            speaker: Speaker ID (0-5). Default: 5 (en_5)
            reload_interval: Model reload interval. Default: 100
            device: Torch device ("cpu" or "cuda"). Default: auto-detect
        """
        self._speaker = speaker
        self._reload_interval = reload_interval
        self._torch_device = self._get_device(device)
        self._tts_model = None
        self._generation_count = 0

        self._load_model()

    def synthesize(self, text: str) -> bytes:
        """Synthesize full audio from text.

        Args:
            text: Text to synthesize

        Returns:
            Complete WAV audio data (24kHz, mono)
        """

    async def astream_synthesize(self, text: str, interrupted_callback: Optional[callable] = None) -> AsyncIterator[TTSChunk]:
        """Stream synthesized audio in chunks.

        Args:
            text: Text to synthesize
            interrupted_callback: Optional callable that returns bool for interruption check

        Yields:
            TTSChunk with audio data
        """

    def _load_model(self) -> None:
        """Load Pocket TTS model from HuggingFace."""

    def _reload_model(self) -> None:
        """Reload model to prevent memory leaks."""

    @staticmethod
    def _get_device(device: Optional[str]) -> torch.device:
        """Get torch device, auto-detect if not specified."""

    def _chunk_audio(self, audio_tensor: torch.Tensor) -> list[torch.Tensor]:
        """Split audio into 500ms chunks."""
```

---

## 1.5 API Contract

### Internal Interface

| Method | Input | Output | Description |
|--------|-------|--------|-------------|
| `synthesize()` | `text: str` | `bytes` | Synthesize full audio (blocking) |
| `astream_synthesize()` | `text: str, interrupted_callback: callable` | `AsyncIterator[TTSChunk]` | Stream audio chunks with interruption |

### Usage Example

```python
# File: application/use_cases/voice_pipeline_use_case.py
from infrastructure.external.tts_service import TTSService, TTSChunk

tts_service = TTSService(speaker=5, reload_interval=100)

async def speak_response(text: str, session: VoiceSessionEntity) -> None:
    """Stream TTS output with interruption support."""

    # Define interruption callback
    def is_interrupted() -> bool:
        return session.interrupted

    # Stream audio chunks
    async for chunk in tts_service.astream_synthesize(text, is_interrupted):
        if session.interrupted:
            logger.info("TTS interrupted")
            break

        # Send chunk via WebSocket
        await websocket_manager.send_message(
            session.session_id,
            WebSocketMessageType.RESPONSE_AUDIO,
            {
                "audio_bytes": base64.b64encode(chunk.audio_bytes).decode(),
                "sample_rate": chunk.sample_rate,
                "is_interrupted": False,
            }
        )
```

---

## 1.6 Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-TTS-001 | Audio chunks MUST be 500ms (12000 samples @ 24kHz) | TTSService.CHUNK_SAMPLES |
| BR-TTS-002 | Model MUST reload every N generations | TTSService._reload_model() |
| BR-TTS-003 | Interrupt flag MUST be checked in synthesis loop | astream_synthesize() callback |
| BR-TTS-004 | Output MUST be 24kHz sample rate | TTSService.TTS_SAMPLE_RATE |

---

## 1.7 Acceptance Criteria

- [ ] TTSService loads Pocket TTS model on startup
- [ ] Text is synthesized to audio at 24kHz sample rate
- [ ] Audio is streamed in 500ms chunks
- [ ] Each chunk includes audio_bytes, chunk_index, is_final
- [ ] Interruption callback is checked during synthesis
- [ ] Interruption terminates synthesis within 200ms
- [ ] Model reloads every N generations (default: 100)
- [ ] Memory usage stays under 2GB after 1 hour
- [ ] First chunk latency <100ms
- [ ] Auto-detects CUDA if available
- [ ] Thread-safe for concurrent access
- [ ] Empty text returns empty audio (not error)

---

## 1.8 Configuration

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `speaker` | 5 | 0-5 | Speaker ID (en_0 to en_5) |
| `reload_interval` | 100 | 10-1000 | Model reload interval (number of synthesize calls) |
| `chunk_ms` | 500 | 100-1000 | Audio chunk size in milliseconds |
| `device` | auto | cpu/cuda | Torch device for inference |

---

## 1.9 Model Specifications

| Property | Value | Source |
|----------|-------|--------|
| **Model Name** | kyutai/pocket-tts | HuggingFace |
| **Parameters** | 100M | Model spec |
| **Sample Rate** | 24kHz or 48kHz | Model output |
| **Channels** | Mono (1) | Model output |
| **Speakers** | 6 (English) | Model capability |
| **Model Size** | ~400MB | Disk space |
| **Memory** | ~2GB | Runtime (without reload) |
| **Latency** | <200ms | Measured |

---

## 1.10 Memory Management Strategy

**Problem**: Pocket TTS model grows unbounded (observed 32GB+ in R011)

**Solution**: Periodic model reload

| Metric | Value | Rationale |
|--------|-------|-----------|
| **Reload Interval** | 100 generations | Balances memory vs performance |
| **Expected Memory** | <2GB | With reload every 100 calls |
| **Reload Time** | <1s | Model loading overhead |
| **Detection** | Monitor memory usage | Can adjust interval dynamically |

---

**Related Specs**:
- `specs/voice-pipeline/spec.md` - Voice pipeline orchestration
- research/08_tts_stt_integration.md - TTS patterns and memory management
