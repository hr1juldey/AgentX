# AGENTX Kyutai Speech Integration Plan

**Version**: 1.0.0
**Date**: 2026-01-18
**Status**: Draft
**Replaces**: Previous PRD (different task)

---

## 1. Objective

Replace Silero STT/TTS with Kyutai's advanced speech models (unmute STT + pocket-tts TTS) deployed as independent Docker containers with fast communication to main AGENTX container.

**Key Goals**:
- Achieve sub-300ms voice-to-voice latency for natural conversation
- Deploy speech models as isolated containers
- Enable future visual cortex plugin (webcam/YOLO/VL-JEPA)
- Support DSPy ReAct chains with Ollama LLMs

---

## 2. Kyutai Architecture Summary

### 2.1 Component Overview

| Component | Repository | Language | Latency | Hardware | Notes |
|-----------|------------|----------|---------|----------|-------|
| **unmute STT** | `kyutai-labs/unmute` | Python + Rust | 500ms (1B) / 2.5s (2.6B) | GPU (16GB+) | OpenAI Realtime API protocol |
| **pocket-tts** | `kyutai-labs/pocket-tts` | Python | ~200ms first chunk | CPU (2 cores) | FastAPI, streaming |
| **DSM Core** | `kyutai-labs/delayed-streams-modeling` | Python/MLX | N/A | GPU/Apple Silicon | Research framework |

### 2.2 Key Innovations

**Delayed Streams Modeling (DSM)**:
- Dual-stream architecture: audio and text modeled "next to" each other
- Self-pacing via "inner monologue" tokens
- Bidirectional: same architecture does STT or TTS
- Streaming-first design

**Performance Advantages over Silero**:
| Metric | Silero | Kyutai | Improvement |
|--------|--------|--------|-------------|
| **STT Latency** | 800-1000ms | 500ms | 2x faster |
| **TTS Latency** | 300-500ms | 200ms | 2.5x faster |
| **Throughput** | 1 stream | 400 streams (H100) | 400x |
| **VAD** | Separate model | Built-in semantic VAD | Integrated |

---

## 3. Docker Compose Architecture

### 3.1 Container Structure

```yaml
# docker-compose.yml
services:
  # Main AGENTX orchestrator
  agentx:
    build: ./agentx
    ports:
      - "8000:8000"  # FastAPI
      - "8500:8500"  # WebSocket voice
    environment:
      - KYUTAI_STT_URL=http://kyutai-stt:8765/v1/realtime
      - KYUTAI_TTS_URL=http://kyutai-tts:8000
    depends_on:
      - kyutai-stt
      - kyutai-tts
      - ollama
      - qdrant

  # Kyutai unmute STT (Rust server)
  kyutai-stt:
    image: ghcr.io/kyutai-labs/moshi-server:latest
    ports:
      - "8765:8765"  # OpenAI Realtime API
    environment:
      - NVIDIA_VISIBLE_DEVICES=0
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    volumes:
      - ./models:/models:ro  # Model cache

  # Kyutai pocket-tts TTS (Python)
  kyutai-tts:
    build: ./kyutai-tts
    ports:
      - "8001:8000"  # FastAPI
    environment:
      - FIRST_CHUNK_LENGTH_SECONDS=0.2
    # CPU-only, no GPU needed
    restart: unless-stopped

  # Ollama LLM server
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama

  # Qdrant vector DB
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage

  # Future: Visual cortex plugin
  visual-cortex:
    build: ./plugins/visual-cortex
    ports:
      - "8002:8000"
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    volumes:
      - /dev/video0:/dev/video0  # Webcam access

volumes:
  ollama_data:
  qdrant_data:
```

---

## 4. Communication Protocols

### 4.1 STT Communication (WebSocket)

**Protocol**: OpenAI Realtime API (ORA) compatible

**AGENTX → Kyutai STT**:
```javascript
// Connect to Kyutai STT
const ws = new WebSocket('ws://kyutai-stt:8765/v1/realtime', 'realtime');

// Send audio chunks
ws.send(JSON.stringify({
  type: "input_audio_buffer.append",
  audio: base64_encoded_opus_audio  // 24kHz Opus
}));

// Configure session
ws.send(JSON.stringify({
  type: "session.update",
  session: {
    turn_detection: {
      type: "semantic_vad",
      threshold: 0.5,
      prefix_padding_ms: 300,
      silence_duration_ms: 500
    }
  }
}));
```

**Kyutai STT → AGENTX**:
```javascript
// Receive transcription
{
  type: "conversation.item.input_audio_transcription.delta",
  delta: "hello world"
}

// Speech detected event
{
  type: "input_speech_started",
  audio_start_ms: 1234
}

// Speech ended event (with built-in VAD)
{
  type: "input_speech_stopped",
  audio_end_ms: 4567
}
```

### 4.2 TTS Communication (HTTP/WebSocket)

**Protocol**: FastAPI HTTP + StreamingResponse

**AGENTX → Kyutai TTS**:
```python
import httpx

async def generate_speech(text: str, voice_url: str = None):
    async with httpx.AsyncClient() as client:
        async with client.stream(
            'POST',
            'http://kyutai-tts:8000/tts',
            json={
                'text': text,
                'voice_url': voice_url or 'hf://kyutai/tts-voices/alba-mackenna/casual.wav'
            },
            timeout=30.0
        ) as response:
            async for chunk in response.aiter_bytes():
                # Stream WAV chunks (24kHz)
                yield chunk
```

**FastAPI Alternative (WebSocket streaming)**:
```python
# In kyutai-tts container
from fastapi import WebSocket

@app.websocket("/ws/tts")
async def tts_websocket(websocket: WebSocket):
    await websocket.accept()

    while True:
        data = await websocket.receive_json()
        text = data.get('text')

        # Stream generation
        for chunk in generate_audio_stream(text):
            await websocket.send_bytes(chunk)
```

### 4.3 Inter-Container Optimization

**Option A: Shared Network**
```yaml
# All containers on same Docker network
networks:
  agentx-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16  # Fast local network
```

**Option B: Unix Socket (for ultra-low latency)**
```yaml
# Shared volume for socket
volumes:
  - socket_volume:/tmp/sockets

# In AGENTX
socket_url = "http://tmp/sockets/kyutai-stt.sock"

# In kyutai-stt
bind = "unix:///tmp/sockets/kyutai-stt.sock"
```

---

## 5. AGENTX Integration Changes

### 5.1 Replace Silero Services

**Current Structure** (to be replaced):
```
R011_personal_assistant/backend/services/
├── stt_service.py   # Silero STT
├── tts_service.py   # Silero TTS
└── vad_service.py   # Silero VAD
```

**New Structure**:
```
agentx/services/
├── kyutai_client.py  # Unified Kyutai interface
├── voice_orchestrator.py  # Voice pipeline coordination
└── protocols/
    ├── ora_client.py  # OpenAI Realtime API client
    └── pocket_tts_client.py  # Pocket TTS HTTP client
```

### 5.2 Kyutai Client Implementation

```python
# agentx/services/kyutai_client.py
import httpx
import json
import asyncio
import websockets
from typing import AsyncGenerator

class KyutaiSTTClient:
    """Client for Kyutai unmute STT via OpenAI Realtime API."""

    def __init__(self, url: str = "ws://kyutai-stt:8765/v1/realtime"):
        self.url = url
        self.ws = None

    async def connect(self):
        """Establish WebSocket connection."""
        self.ws = await websockets.connect(
            self.url,
            subprotocols=['realtime']
        )

        # Configure session with semantic VAD
        await self.send({
            "type": "session.update",
            "session": {
                "turn_detection": {
                    "type": "semantic_vad",
                    "threshold": 0.5,
                    "prefix_padding_ms": 300,
                    "silence_duration_ms": 500
                }
            }
        })

    async def stream_audio(self, audio_chunks: AsyncGenerator[bytes, None]):
        """Stream audio for transcription."""
        async for chunk in audio_chunks:
            await self.send({
                "type": "input_audio_buffer.append",
                "audio": base64.b64encode(chunk).decode()
            })

    async def transcriptions(self) -> AsyncGenerator[str, None]:
        """Receive transcription stream."""
        async for message in self.ws:
            data = json.loads(message)

            if data['type'] == 'conversation.item.input_audio_transcription.delta':
                yield data['delta']

            elif data['type'] == 'input_speech_stopped':
                # VAD detected speech end
                break

    async def send(self, data: dict):
        """Send message to WebSocket."""
        await self.ws.send(json.dumps(data))

class KyutaiTTSClient:
    """Client for Kyutai pocket-tts."""

    def __init__(self, url: str = "http://kyutai-tts:8000"):
        self.url = url

    async def generate_stream(
        self,
        text: str,
        voice_url: str = None
    ) -> AsyncGenerator[bytes, None]:
        """Stream TTS audio."""
        async with httpx.AsyncClient() as client:
            async with client.stream(
                'POST',
                f'{self.url}/tts',
                json={
                    'text': text,
                    'voice_url': voice_url or 'hf://kyutai/tts-voices/alba-mackenna/casual.wav'
                },
                timeout=30.0
            ) as response:
                async for chunk in response.aiter_bytes():
                    yield chunk
```

### 5.3 Voice Orchestrator

```python
# agentx/services/voice_orchestrator.py
from fastapi import WebSocket
import asyncio

class VoiceOrchestrator:
    """Coordinates STT, LLM, and TTS for voice conversation."""

    def __init__(self, stt_client, tts_client, dspy_agent):
        self.stt = stt_client
        self.tts = tts_client
        self.agent = dspy_agent

        # State
        self.is_speaking = False
        self.interrupted = False
        self.audio_buffer = []

    async def handle_websocket(self, websocket: WebSocket):
        """Main voice interaction loop."""
        await websocket.accept()

        # Connect to STT
        await self.stt.connect()

        # Background tasks
        stt_task = asyncio.create_task(self._stt_loop(websocket))
        llm_task = asyncio.create_task(self._llm_loop())
        tts_task = asyncio.create_task(self._tts_loop(websocket))

        try:
            await asyncio.gather(stt_task, llm_task, tts_task)
        finally:
            stt_task.cancel()
            llm_task.cancel()
            tts_task.cancel()

    async def _stt_loop(self, websocket: WebSocket):
        """Receive audio, send to STT, collect transcription."""
        async for audio_chunk in self._receive_audio(websocket):
            await self.stt.stream_audio(self._chunk_generator(audio_chunk))

        # Collect transcription
        user_text = ""
        async for chunk in self.stt.transcriptions():
            user_text += chunk

            # Check for interruption
            if self.is_speaking:
                self.interrupted = True

        # Send to LLM queue
        await self.llm_queue.put(user_text)

    async def _llm_loop(self):
        """Process transcriptions with DSPy agent."""
        while True:
            user_text = await self.llm_queue.get()

            # DSPy ReAct chain with Ollama
            response = await self.agent.respond(user_text)

            await self.tts_queue.put(response)

    async def _tts_loop(self, websocket: WebSocket):
        """Generate TTS and stream to client."""
        while True:
            text = await self.tts_queue.get()

            self.is_speaking = True
            self.interrupted = False

            async for audio_chunk in self.tts.generate_stream(text):
                if self.interrupted:
                    break

                await websocket.send_bytes(audio_chunk)

            self.is_speaking = False
```

---

## 6. Implementation Phases

### Phase 1: Docker Infrastructure (Week 1)

**Tasks**:
1. Create `docker/kyutai-stt/Dockerfile` for unmute STT
2. Create `docker/kyutai-tts/Dockerfile` for pocket-tts
3. Update `docker-compose.yml` with all services
4. Configure networking for low-latency communication
5. Test container-to-container communication

**Files to Create**:
- `docker/kyutai-stt/Dockerfile`
- `docker/kyutai-tts/Dockerfile`
- `docker-compose.yml`

**Verification**:
```bash
docker-compose up -d
curl http://localhost:8001/health  # TTS health check
wscat -c ws://localhost:8765/v1/realtime  # STT connection
```

### Phase 2: Client Libraries (Week 1-2)

**Tasks**:
1. Implement `KyutaiSTTClient` class
2. Implement `KyutaiTTSClient` class
3. Create protocol adapters for ORA and HTTP
4. Write unit tests for clients

**Files to Create/Modify**:
- `agentx/services/protocols/ora_client.py`
- `agentx/services/protocols/pocket_tts_client.py`
- `agentx/services/kyutai_client.py`
- `tests/services/test_kyutai_client.py`

**Verification**:
```python
# Test STT client
stt = KyutaiSTTClient()
await stt.connect()
# Send test audio, verify transcription

# Test TTS client
tts = KyutaiTTSClient()
chunks = [chunk async for chunk in tts.generate_stream("hello")]
# Verify WAV format
```

### Phase 3: Voice Pipeline Integration (Week 2)

**Tasks**:
1. Implement `VoiceOrchestrator`
2. Replace Silero services in main API
3. Update WebSocket voice endpoint
4. Integrate with DSPy ReAct agent
5. Add interruption handling

**Files to Modify**:
- `agentx/api/routes.py` (update `/ws/voice`)
- `agentx/main.py` (wire up dependencies)

**Verification**:
```bash
# End-to-end voice test
python -m tests.e2e.test_voice_pipeline

# Measure latency
# Target: <300ms voice-to-voice
```

### Phase 4: DSPy Integration (Week 2-3)

**Tasks**:
1. Create DSPy ReAct agent with tools
2. Connect voice orchestrator to DSPy
3. Add tool execution (calculator, search, etc.)
4. Test multi-tool chains

**Files to Create**:
- `agentx/agents/dspy_agent.py`
- `agentx/tools/`
- `agentx/tools/__init__.py`

**Verification**:
```python
# Test DSPy chain
agent = DSPyAgent()
result = agent.respond("What's 123 * 456?")
# Should call calculator tool
```

### Phase 5: Visual Cortex Plugin (Future)

**Tasks**:
1. Create `plugins/visual-cortex/` directory
2. Implement OpenCV frame capture
3. Integrate YOLO for object detection
4. Add VL-JEPA model for scene understanding
5. Create WebSocket streaming interface

**Architecture**:
```
Webcam → OpenCV → YOLO Detection → VL-JEPA → Scene Context → DSPy
                ↓
           Object Labels
                ↓
          Spatial Features
                ↓
           Action Understanding
```

**Files to Create**:
- `plugins/visual-cortex/Dockerfile`
- `plugins/visual-cortex/camera.py`
- `plugins/visual-cortex/detector.py`
- `plugins/visual-cortex/vision_transformer.py`
- `plugins/visual-cortex/api.py`

---

## 7. Configuration

### 7.1 Environment Variables

```bash
# AGENTX Main Container
KYUTAI_STT_URL=ws://kyutai-stt:8765/v1/realtime
KYUTAI_TTS_URL=http://kyutai-tts:8000
KYUTAI_STT_MODEL=stt-1b-en_fr  # or stt-2.6b-en
KYUTAI_TTS_VOICE=hf://kyutai/tts-voices/alba-mackenna/casual.wav

# Kyutai STT Container
HF_TOKEN=your_huggingface_token
NVIDIA_VISIBLE_DEVICES=0

# Kyutai TTS Container
FIRST_CHUNK_LENGTH_SECONDS=0.2
MAX_VOICE_CACHE_SIZE=10
```

### 7.2 Model Configuration

**STT Model Selection**:
```yaml
stt:
  model: "stt-1b-en_fr"  # Fast, bilingual
  # model: "stt-2.6b-en"  # Slower, higher accuracy
  vad:
    type: "semantic"  # Built-in semantic VAD
    threshold: 0.5
    silence_duration_ms: 500
```

**TTS Model Selection**:
```yaml
tts:
  voice: "alba-mackenna/casual"  # Default voice
  # voice: "josephina/casual"
  # voice: "custom"  # For cloned voices
  sample_rate: 24000
  streaming: true
```

---

## 8. Latency Budget

### 8.1 Target: <300ms End-to-End

| Component | Target | Notes |
|-----------|--------|-------|
| **VAD** | 50ms | Built-in semantic VAD |
| **STT (streaming)** | 100ms | First tokens arrive quickly |
| **LLM (first token)** | 50ms | DSPy + Ollama |
| **TTS (first chunk)** | 100ms | Pocket TTS ~200ms, optimize to 100ms |
| **Network** | 0ms | Local container communication |
| **Total** | **300ms** | Target achieved |

### 8.2 Optimization Strategies

1. **Use semantic VAD**: Eliminates separate VAD model
2. **Streaming STT**: Don't wait for full transcription
3. **LLM streaming**: Send tokens as they arrive
4. **TTS parallelism**: Start TTS while LLM still generating
5. **Shared memory**: Use Unix sockets for container communication

---

## 9. Testing Strategy

### 9.1 Unit Tests

```python
# tests/services/test_kyutai_stt_client.py
async def test_stt_client_connection():
    client = KyutaiSTTClient()
    await client.connect()
    assert client.ws is not None
    await client.close()

# tests/services/test_kyutai_tts_client.py
async def test_tts_client_generation():
    client = KyutaiTTSClient()
    chunks = []
    async for chunk in client.generate_stream("test"):
        chunks.append(chunk)
    assert len(chunks) > 0
```

### 9.2 Integration Tests

```python
# tests/integration/test_voice_pipeline.py
async def test_voice_to_voice_latency():
    orchestrator = VoiceOrchestrator(stt, tts, agent)

    # Mock audio input
    audio = load_test_audio("test.wav")

    # Measure latency
    start = time.time()
    result = await orchestrator.process(audio)
    latency = time.time() - start

    assert latency < 0.3  # 300ms
```

### 9.3 End-to-End Tests

```bash
# Manual test with real audio
python -m tests.e2e.test_real_conversation

# Expected: Natural conversation with <300ms response time
```

---

## 10. Critical Success Factors

### 10.1 DO's

✅ **DO** use Kyutai's built-in semantic VAD (eliminates separate VAD)
✅ **DO** deploy speech models in separate containers
✅ **DO** use WebSocket for streaming (not HTTP polling)
✅ **DO** implement interruption handling early
✅ **DO** test with real audio (not synthetic)
✅ **DO** monitor latency through the entire pipeline
✅ **DO** use DSPy for LLM orchestration
✅ **DO** implement graceful degradation

### 10.2 DON'Ts

❌ **DON'T** run speech models in same container as AGENTX
❌ **DON'T** use Silero anymore (Kyutai is superior)
❌ **DON'T** ignore memory management (pocket-tts has known issues)
❌ **DON'T** forget to handle interruptions
❌ **DON'T** use HTTP for STT (WebSocket required)
❌ **DON'T** skip integration tests
❌ **DON'T** assume 24kHz audio (verify format)

---

## 11. Rollout Plan

### Week 1: Infrastructure
- Set up Docker Compose
- Build Kyutai containers
- Test container communication
- Implement client libraries

### Week 2: Integration
- Replace Silero services
- Implement voice orchestrator
- Integrate with DSPy
- Test voice pipeline

### Week 3: Optimization
- Tune latency
- Add interruption handling
- Memory management
- Performance testing

### Week 4: Production Readiness
- Monitoring and metrics
- Error handling
- Documentation
- User testing

---

## 12. Future Extensions

### 12.1 Visual Cortex Plugin

**Architecture**:
```
Webcam → OpenCV Capture → YOLO Detection → VL-JEPA → Scene Context
                                         ↓
                                    DSPy Agent
```

**Container**: `plugins/visual-cortex/`
**GPU Required**: Yes
**Latency Target**: <500ms for scene understanding

### 12.2 Multi-Modal DSPy

**Chain Example**:
```python
# DSPy chain with voice + vision
agent = dspy.ReAct(
    "question->answer",
    tools=[
        voice_tool,      # Kyutai STT/TTS
        vision_tool,     # Visual cortex
        calculator_tool,
        search_tool,
    ]
)
```

---

## 13. References

- [unmute GitHub](https://github.com/kyutai-labs/unmute)
- [pocket-tts GitHub](https://github.com/kyutai-labs/pocket-tts)
- [delayed-streams-modeling](https://github.com/kyutai-labs/delayed-streams-modeling)
- [OpenAI Realtime API](https://platform.openai.com/docs/api-reference/realtime)
- [DSPy Documentation](https://dspy-docs.vercel.app/)
- [AGENTX Research](../research/)

---

**Next Steps**: Review and approve plan, then begin Phase 1 implementation.
