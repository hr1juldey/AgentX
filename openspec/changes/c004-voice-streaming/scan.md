# Scan Artifact: c004-voice-streaming

**Generated**: 2026-01-28
**Change**: c004-voice-streaming
**Schema**: spec-factory v1

---

## 1. LLD Synthesis

### 1.1 Relevant LLD Documents

| Document | Path | Relevance |
|----------|------|-----------|
| TTS/STT Integration Research | `docs/research/08_tts_stt_integration.md` | **PRIMARY** - Voice pipeline architecture, patterns, best practices |
| Infrastructure Adapters LLD | `docs/engineering/lld/infrastructure_adapters.md` | **PRIMARY** - WebSocket Manager, Ollama adapter definitions (LOCKED) |
| Incremental Release Plan | `docs/engineering/lld/incremental_release_plan.md` | **PRIMARY** - Phase 3 (UI + Streaming) with voice endpoints |

### 1.2 Locked Definitions from LLD

**WebSocket Manager** (infrastructure_adapters.md:716-828):

```python
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

**Ollama LLM Adapter** (infrastructure_adapters.md:500-612):

```python
class OllamaLLMAdapter:
    """Ollama LLM adapter for DSPy integration.

    Supports models: gemma3:4b, llama3.2, llava, qwen2.5-coder
    """

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "gemma3:4b", timeout_seconds: int = 120)
    def get_dspy_lm(self) -> dspy.LM
    async def generate_response(self, prompt: str, context: List[Dict[str, str]]) -> str
    async def stream_response(self, prompt: str, context: List[Dict[str, str]]) -> AsyncIterator[str]
    async def embed(self, text: str) -> List[float]
```

### 1.3 Voice Pipeline Patterns (from Research)

**Key Models**:
- **TTS**: Pocket TTS (`kyutai/pocket-tts`) - 100M parameters, CPU-only, 200ms latency
- **STT**: Kyutai STT 2.6B (`kyutai/stt-2.6b-en`) - streaming transcription
- **VAD**: Silero VAD - low latency (<50ms), probability-based

**Three Pipeline Patterns**:
1. **Simple Pipeline** (500-1000ms) - Audio → VAD → STT → LLM → TTS
2. **Streaming Pipeline** (300-500ms) - Full streaming with queues
3. **Interruptible Pipeline** (200-400ms) - Full duplex with interruption handling

---

## 2. Codebase Exploration (opsx:explore)

### 2.1 Exploration Topics

```
Forced Topics:
1. Voice streaming patterns (STT/TTS/VAD)
2. WebSocket bidirectional communication
3. Audio buffering and queue management
4. Interruption handling (full duplex)
5. Integration with C003 agent pipeline
```

### 2.2 File Inventory

#### Backend Files (Prototypes)

| File | Lines | Purpose |
|------|-------|---------|
| `prototypes/R011_personal_assistant/backend/service.py` | 216 | DSPy + Voice integration (STT/TTS services) |
| `prototypes/R011_personal_assistant/backend/stt_service.py` | 100 | Silero VAD + STT implementation |
| `prototypes/R011_personal_assistant/backend/tts_service.py` | 80 | Silero TTS implementation |
| `prototypes/R011_personal_assistant/backend/voice_routes.py` | 60 | WebSocket voice endpoints |

#### Frontend Files (Prototypes)

| File | Lines | Purpose |
|------|-------|---------|
| `prototypes/R011_personal_assistant/frontend/src/components/VoiceAssistant.tsx` | 200 | Voice UI with recording/playback |

---

## 3. Patterns Discovered

### 3.1 Architectural Patterns

**WebSocket Bidirectional Streaming**:
```
Client (Browser/Phone)
    ↕ WebSocket (Port 8016)
Server (FastAPI)
    ↕ asyncio.Queue
STT Worker ─────────┐
    ↓              │
LLM Worker ──────────┤ Streaming Pipeline
    ↓              │
TTS Worker ─────────┘
    ↓
Audio Queue
    ↕ WebSocket
Client
```

**Voice Pipeline Flow**:
```
Audio Input → VAD (Silero) → Buffer → STT (Kyutai) → LLM (DSPy) → TTS (Pocket) → Audio Output
```

### 3.2 Code Patterns

**Silero VAD Integration**:
```python
from silero_vad import VAD

vad_model = load_silero_vad()
speech_prob = vad_model(torch_tensor(audio_np).float().to(_torch_device), sr=16000).item()
```

**Silero TTS Integration**:
```python
from silero import silero_tts

tts_result = silero_tts(language="en", speaker="v3_en")
if isinstance(tts_result, tuple) and len(tts_result) >= 2:
    tts_model = tts_result[0]
    tts_example_text = tts_result[1]
else:
    tts_model = tts_result
    tts_example_text = "Hello world"

audio = tts_model.apply_tts(text=text, speaker="en_5", sample_rate=24000)
```

**Audio Resampling**:
```python
# STT requires 16kHz
if sr != 16000:
    from torchaudio.transforms import Resample
    resampler = Resample(sr, 16000)
    audio_tensor = resampler(audio_tensor)
```

### 3.3 Anti-Patterns to Avoid

| Anti-Pattern | Why Avoid | Alternative |
|--------------|-----------|-------------|
| **Buffering silence** | Increases latency, wastes memory | Use VAD to filter |
| **Blocking TTS generation** | Blocks interruption, poor UX | Stream TTS output |
| **Turn-based only** | Can't interrupt, feels unnatural | Full duplex with VAD monitoring |
| **Large audio chunks** | High latency, slow interruption | 500ms chunks (0.5s @ 24kHz) |
| **Memory leaks in TTS** | Pocket TTS grows to 32GB+ | Reload model periodically |

---

## 4. Reference Analysis

### 4.1 R011 Reference (Voice Patterns)

| Concept | R011 Approach | Improved Approach |
|----------|---------------|-------------------|
| **STT service** | Combined STT + VAD in one file | Split: VADService, STTService |
| **TTS service** | Basic Silero TTS | Add memory management (reload strategy) |
| **WebSocket handling** | Single task | Full duplex: input_task + output_task |
| **Interruption** | Not implemented | Add VAD monitoring during speech |

### 4.2 Research Extracted Patterns

**Best Practices**:
1. **Always use VAD** - Don't buffer silence
2. **Stream everything** - STT, LLM, TTS all streaming
3. **Appropriate buffer sizes** - 500ms chunks for audio
4. **Handle interruptions gracefully** - Check `self.interrupted` regularly
5. **Monitor memory** - Reload TTS model periodically

---

## 5. Key Files for This Change

```
# Research Documents (PRIMARY)
/home/riju279/Documents/Code/XRIG/AgentX/docs/research/08_tts_stt_integration.md

# LLD Documents (LOCKED)
/home/riju279/Documents/Code/XRIG/AgentX/docs/engineering/lld/infrastructure_adapters.md

# Prototype References (Concepts Only)
/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R011_personal_assistant/

# Dependency Artifacts
/home/riju279/Documents/Code/XRIG/AgentX/openspec/changes/c002-data-contracts/ (WebSocket messages)
/home/riju279/Documents/Code/XRIG/AgentX/openspec/changes/c003-agent-pipeline/ (Agent pipeline integration)
```

---

**Next Artifact**: extract.md
