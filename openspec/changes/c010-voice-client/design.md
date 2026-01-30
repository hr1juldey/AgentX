# Design Artifact: c010-voice-client

**Generated**: 2026-01-29
**Change**: c010-voice-client
**Schema**: spec-driven v1

---

## Context

### Background

Current c004-voice-streaming implements voice services (VAD, STT, TTS) as internal AgentX components. This requires managing PyTorch models, audio processing pipelines, and WebSocket protocols directly within AgentX. However, kyutai voice-server already exists as a production-ready external service on port 16000 that handles these concerns efficiently.

### Current State (c004)

**Internal Service Architecture**:
```
Frontend → AgentX WebSocket → VoicePipelineUseCase
                                      ↓
                         ┌────────────┼────────────┐
                         ↓            ↓            ↓
                    VADService   STTService   TTSService
                         ↓            ↓            ↓
                    Silero VAD   Kyutai STT   Pocket TTS
```

**Problems**:
- Model management complexity (PyTorch, transformers, silero dependencies)
- Memory leaks in TTS (observed 32GB+ in R011)
- Duplicates kyutai's capabilities
- Harder to update models (requires AgentX deployment)

### Target State (c010)

**External Service Architecture**:
```
Frontend → AgentX WebSocket → VoiceGatewayService → Kyutai Server (port 16000)
                                      ↓                              ↓
                            ConversationalState         STT (moshi)
                                      ↓                              ↓
                            C003 AgentPipeline          TTS (pocket-tts)
                                                               ↓
                                                         VAD (silero)
```

### Constraints

- **Kyutai Protocol**: Must match kyutai WebSocket message format exactly
- **Latency**: <500ms end-to-end target (same as c004)
- **CLAUDE_POLICY.md**: File size limits, absolute imports, ruff compliance
- **Dependencies**: C001 (folder structure), C002 (data contracts), C003 (agent pipeline), C007 (frontend architecture)

---

## Goals / Non-Goals

### Goals

- **Fast async text stream handling**: Efficiently route text between frontend and kyutai server
- **Conversational state management**: Track history, context, and session state
- **Error handling and reconnection**: Graceful degradation when kyutai unavailable
- **Clean separation**: AgentX focuses on text/context, kyutai handles audio/models
- **Protocol alignment**: Match kyutai message format exactly

### Non-Goals

- **Voice model management**: Kyutai handles model loading, optimization
- **Audio processing**: Kyutai handles resampling, format conversion
- **VAD tuning**: Kyutai handles speech detection thresholds
- **Voice wake word**: "Hey AgentX" activation (future feature)
- **Speaker recognition**: User identification via voice (future feature)

---

## Decisions

### Decision 1: External vs Internal Voice Services

**Choice**: Use external kyutai voice-server

**Rationale**:

| Factor | Internal (c004) | External (c010) |
|--------|-----------------|-----------------|
| Model Management | AgentX manages models | Kyutai manages models |
| Memory Leaks | Observed in R011 (32GB+) | Kyutai handles reload |
| Updates | Requires AgentX deploy | Independent updates |
| Dependency Weight | torch (~2GB), transformers (~500MB) | websockets (~100KB) |
| Latency | Same (both use WebSocket) | Same |
| Quality | Same models | Same models |

**Trade-off**: Adds external dependency on kyutai service

**Alternatives Considered**:
- **Internal services (c004)**: Duplicate effort, maintenance burden
- **Cloud APIs (ElevenLabs, AssemblyAI)**: Paid, higher latency, privacy concerns
- **Hybrid**: Internal fallback - adds complexity, defeats purpose

### Decision 2: Protocol Alignment - Match Kyutai Exactly

**Choice**: Use kyutai message format directly in AgentX

**Rationale**:

- **Simplicity**: No protocol translation layer = less complexity
- **Performance**: Direct passthrough = lower latency
- **Compatibility**: Works with existing kyutai clients
- **Updates**: Kyutai protocol changes propagate automatically

**Kyutai Message Format**:
```json
{
  "type": "Config|Audio|Text|Error|Eos|Heartbeat",
  "data": "<base64 audio for Audio, text for Text, error message for Error>",
  "session_id": "uuid",
  "timestamp": 1234567890.123,
  "metadata": {}  // Optional
}
```

**Alternatives Considered**:
- **AgentX wrapper protocol**: Add translation layer (rejected - adds latency)
- **Protocol adapter**: Translate kyutai → AgentX → kyutai (rejected - double conversion)

### Decision 3: Conversational State in AgentX, Not Kyutai

**Choice**: Store conversation history and context in AgentX, not kyutai

**Rationale**:

- **Domain relevance**: Conversation state is AgentX's domain (C003 agent pipeline)
- **Flexibility**: AgentX can inject context into queries, use for RAG
- **Persistence**: AgentX controls storage (Redis, database)
- **Isolation**: Kyutai remains stateless audio processor

**State Storage**:
```python
@dataclass
class ConversationSession:
    session_id: UUID
    messages: list[ConversationMessage]
    context: ConversationContext
    created_at: datetime
    last_activity_at: datetime

@dataclass
class ConversationMessage:
    message_id: UUID
    role: "user" | "assistant"
    content: str
    timestamp: datetime
    metadata: dict | None = None

@dataclass
class ConversationContext:
    current_topic: str | None = None
    entities: dict[str, Any] | None = None
    sentiment: str | None = None
    language: str = "en"
    timezone: str = "UTC"
```

**Alternatives Considered**:
- **Store in kyutai**: Locks into kyutai implementation (rejected)
- **Distributed cache (Redis)**: Adds dependency (future optimization)

### Decision 4: Single WebSocket vs Dual WebSocket

**Choice**: Single WebSocket connection from frontend to AgentX, AgentX manages dual connections to kyutai

**Rationale**:

```
Frontend (Single WebSocket)
    ↓
AgentX VoiceGatewayService
    ↓ (STT WebSocket)
Kyutai STT Endpoint (ws://localhost:16000/api/v1/ws/stt)
    ↓ (TTS WebSocket)
Kyutai TTS Endpoint (ws://localhost:16000/api/v1/ws/tts)
```

- **Simplicity**: Frontend only needs one WebSocket
- **State management**: AgentX can correlate STT ↔ TTS sessions
- **Error handling**: AgentX can manage reconnection to kyutai transparently
- **Context injection**: AgentX can inject conversation context before TTS

**Alternatives Considered**:
- **Dual WebSocket from frontend**: More complex client (rejected)
- **Single kyutai WebSocket**: Not supported by kyutai (separate STT/TTS endpoints)

### Decision 5: Graceful Degradation vs Hard Dependency

**Choice**: Graceful degradation when kyutai unavailable

**Rationale**:

- **Development**: Frontend works without kyutai running
- **Testing**: Can mock kyutai responses
- **Partial functionality**: Text-only mode when voice unavailable

**Degradation Levels**:

| Kyutai State | AgentX Behavior |
|--------------|-----------------|
| Available | Full voice interaction |
| Unavailable | Text-only mode with error message |
| Recovering | Show reconnecting indicator |

**Alternatives Considered**:
- **Hard dependency**: Frontend breaks without kyutai (rejected - poor UX)

### Decision 6: Text Stream Handling - Passthrough vs Buffer

**Choice**: Buffer and debounce text chunks for efficiency

**Rationale**:

- **STT stream**: Kyutai sends partial transcripts, buffer for coherent display
- **TTS stream**: Send complete sentences to kyutai for better prosody
- **Network efficiency**: Fewer WebSocket messages

**Buffer Strategy**:
```python
# STT: Buffer partial transcripts until Eos or punctuation
stt_buffer = []
if message.type == "Text":
    stt_buffer.append(message.data)
    if message.data.endswith((".", "!", "?")) or message.type == "Eos":
        full_transcript = " ".join(stt_buffer)
        send_to_frontend(full_transcript)
        stt_buffer.clear()

# TTS: Send complete sentences
for sentence in split_sentences(llm_response):
    send_to_kyutai_tts(sentence)
```

**Alternatives Considered**:
- **Immediate passthrough**: Too many WebSocket messages (rejected)
- **Full buffering**: Wait for complete response (rejected - higher latency)

### Decision 7: SDK Dependency vs Direct WebSocket Implementation

**Choice**: Hybrid adapter pattern using voice_client SDK as internal dependency

**Rationale**:

After exploring the kyutai voice_client SDK at `/home/riju279/Documents/Tools/kyutai/delayed-streams-modeling/voice_client/`, we identified a production-ready Python SDK with:
- Auto-reconnection with exponential backoff
- Message encoding abstraction (JSON/MsgPack)
- Rich exception hierarchy
- Built-in audio handling (validation, chunking, format conversion)

**Comparison of Three Approaches**:

| Aspect | Direct SDK Dependency | Direct WebSocket (original) | Hybrid Adapter (CHOSEN) |
|--------|---------------------|----------------------------|-------------------------|
| **Code maintenance** | SDK handles reconnection, encoding | AgentX maintains all logic | SDK reliability + AgentX control |
| **External dependencies** | Adds voice_client package | Only websockets | voice_client + websockets fallback |
| **Protocol control** | SDK dictates protocol | AgentX full control | AgentX DTOs remain public API |
| **Session management** | SDK generates UUIDs | AgentX controls lifecycle | Adapter maps SDK ↔ AgentX sessions |
| **Graceful degradation** | SDK failure = hard failure | Custom fallback needed | Feature flag: SDK or direct WS |
| **Frontend support** | No TypeScript SDK | Protocol documented for TS | Adapter layer documents protocol |
| **Testing** | Mock SDK | Test WebSocket directly | Mock SDK or use fallback |
| **Debugging** | Less visibility | Full message visibility | Adapter can log both layers |

**Why Hybrid Adapter Pattern**:

1. **Best of both worlds**: SDK's production-tested reconnection + AgentX's protocol control
2. **Graceful degradation**: Fall back to direct WebSocket if SDK unavailable
3. **Public API stability**: AgentX DTOs remain stable even if SDK changes
4. **Session mapping**: Adapter synchronizes SDK sessions with AgentX conversations
5. **Feature flag support**: `USE_VOICE_SDK=true/false` for A/B testing
6. **Frontend-ready**: Adapter documents protocol for future TypeScript SDK

**Implementation Architecture**:

```python
# VoiceGatewayService uses SDK internally, exposes AgentX DTOs
class VoiceGatewayService:
    def __init__(self, state_manager, text_handler):
        self._state_manager = state_manager
        self._text_handler = text_handler
        self._use_sdk = settings.voice.use_voice_sdk  # Feature flag

    async def handle_session(self, frontend_ws: WebSocket, session_id: UUID):
        if self._use_sdk:
            # Use SDK via adapter
            async with VoiceClient(stt_url=..., tts_url=...) as voice:
                await self._handle_via_sdk(voice, frontend_ws, session_id)
        else:
            # Direct WebSocket (fallback)
            await self._handle_via_direct_ws(frontend_ws, session_id)
```

**SDK Integration Points**:

- **STT**: `STTClient.transcribe()` and `STTClient.stream_transcription()`
- **TTS**: `TTSClient.synthesize()` (async iterator of AudioChunk)
- **Combined**: `VoiceClient.converse()` with agent_callback for C003 integration
- **Reconnection**: Built-in `BaseClient.connect()` with exponential backoff
- **Encoding**: `get_encoder("json")` or `get_encoder("msgpack")`
- **Audio**: `AudioHandler.load_audio_file()`, `validate_audio()`, `chunk_audio()`

**Session Mapping Strategy**:

```python
# Adapter maps SDK sessions to AgentX conversations
_sdk_to_agentx_sessions: dict[str, UUID] = {}

# When SDK creates session:
sdk_session_id = voice.stt.session_id
_sdk_to_agentx_sessions[sdk_session_id] = agentx_session_id

# When SDK sends messages, remap session_id
agentx_message = {
    "type": "Text",
    "data": text,
    "session_id": str(_sdk_to_agentx_sessions[sdk_session_id]),
    "timestamp": time.time()
}
```

**Dependencies Added**:

```toml
# pyproject.toml
dependencies = [
    "voice-client>=0.1.0",  # From local path or PyPI
]
```

**Alternatives Considered**:
- **Direct SDK dependency**: Less control, protocol coupling, harder frontend parity (rejected)
- **Direct WebSocket only**: More maintenance, reinventing reconnection logic (rejected - SDK is proven)

**Risks and Mitigations**:

| Risk | Mitigation |
|------|------------|
| SDK version breaks adapter | Pin SDK version, test before upgrading |
| SDK session_id conflicts | Map SDK sessions to AgentX UUIDs |
| SDK dependency unavailable | Direct WebSocket fallback path |
| Debugging complexity | Add logging at adapter boundaries |
| Frontend has no SDK | Adapter documents protocol for TS implementation |

---

## Risks / Trade-offs

### Risk 1: Kyutai Service Unavailability

**Risk**: Kyutai server crashes or becomes unavailable, breaking voice features

**Mitigation**:
- Graceful degradation to text-only mode
- Health check endpoint (`GET /api/v1/voice/kyutai/status`)
- Automatic reconnection with exponential backoff
- User notification: "Voice unavailable. Using text mode."

### Risk 2: Protocol Mismatch

**Risk**: Kyutai protocol changes break AgentX integration

**Mitigation**:
- Follow kyutai client examples exactly (stt_client.py, tts_client.py)
- Version lock kyutai server in development
- Protocol validation on startup
- Fallback to text mode on protocol error

### Risk 3: Increased Latency

**Risk**: Two WebSocket hops (Frontend → AgentX → Kyutai) increase latency

**Mitigation**:
- AgentX uses async WebSocket for minimal overhead
- Local network (localhost) latency <5ms
- Total latency still <500ms target (same as c004)
- Monitor and optimize in production

### Risk 4: Conversational State Synchronization

**Risk**: Multiple concurrent sessions desynchronize conversation state

**Mitigation**:
- Session ID isolation (UUID)
- In-memory session storage with Redis backup
- Session timeout and cleanup
- Last-write-wins for concurrent updates

### Risk 5: Breaking Changes to c004

**Risk**: Existing c004 implementations break with c010 changes

**Mitigation**:
- Migration path: Phase 1 (coexist) → Phase 2 (deprecate) → Phase 3 (remove)
- Feature flag to enable/disable c010
- Backward compatibility layer during transition
- Clear deprecation notices

---

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Voice Client System (c010)                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Frontend (Browser/Mobile)                                              │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  VoiceClient (lib/voice/client.ts)                              │  │
│  │    - Single WebSocket to AgentX                                 │  │
│  │    - Message routing (STT, TTS, Error)                          │  │
│  │    - Conversation UI (transcript, history)                      │  │
│  │    - Reconnection logic                                         │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                              ↕ WebSocket (port 8019)                   │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Voice Routes (FastAPI)                                         │  │
│  │    - WebSocket /ws/voice                                        │  │
│  │    - GET /api/v1/voice/kyutai/status                            │  │
│  │    - GET /api/v1/voice/conversation/history                     │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                              ↓                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  VoiceGatewayService (Infrastructure Layer)                      │  │
│  │    ┌────────────────────────────────────────────────────────┐    │  │
│  │    │  Voice SDK Adapter (NEW - Decision 7)                   │    │  │
│  │    │    - Wraps voice_client SDK                              │    │  │
│  │    │    - Maps SDK sessions → AgentX sessions                │    │  │
│  │    │    - Feature flag: USE_VOICE_SDK=true/false              │    │  │
│  │    │    - Fallback to direct WebSocket                        │    │  │
│  │    │    ┌────────────────────────────────────────────┐       │    │  │
│  │    │    │ voice_client SDK (internal dependency)      │       │    │  │
│  │    │    │  - VoiceClient (STT+TTS combined)            │       │    │  │
│  │    │    │  - STTClient (streaming transcription)       │       │    │  │
│  │    │    │  - TTSClient (audio synthesis)               │       │    │  │
│  │    │    │  - BaseClient (reconnection, encoding)       │       │    │  │
│  │    │    │  - AudioHandler (chunking, validation)        │       │    │  │
│  │    │    └────────────────────────────────────────────┘       │    │  │
│  │    └────────────────────────────────────────────────────────┘    │  │
│  │                                                                 │  │
│  │    ┌────────────────────────────────────────────────────────┐    │  │
│  │    │  Conversational State Manager                           │    │  │
│  │    │    - Track messages (user, assistant)                   │    │  │
│  │    │    - Manage context (topic, entities)                   │    │  │
│  │    │    - Session persistence                                │    │  │
│  │    └────────────────────────────────────────────────────────┘    │  │
│  │                                                                 │  │
│  │    ┌────────────────────────────────────────────────────────┐    │  │
│  │    │  Text Stream Handler                                    │    │  │
│  │    │    - Buffer STT transcripts                             │    │  │
│  │    │    - Split TTS into sentences                           │    │  │
│  │    │    - Handle interruption                                │    │  │
│  │    └────────────────────────────────────────────────────────┘    │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                              ↓                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  C003 Agent Pipeline Integration                                │  │
│  │    - ExecuteAgentQueryUseCase                                   │  │
│  │    - Inject conversational context                              │  │
│  │    - Return response with UI widgets                            │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                              ↓                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Kyutai Voice Server (External)                                 │  │
│  │    - STT: ws://localhost:16000/api/v1/ws/stt                    │  │
│  │    - TTS: ws://localhost:16000/api/v1/ws/tts                    │  │
│  │    - Models: moshi (STT), pocket-tts (TTS), silero (VAD)        │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Data Flow

#### Voice Request Flow (Speech → Speech)

```
1. Frontend: User speaks into microphone
              ↓
2. VoiceClient: Send Audio message to AgentX WebSocket
              ↓
3. VoiceGatewayService: Route to kyutai STT WebSocket
              ↓
4. Kyutai STT: Transcribe audio → Text messages (streaming)
              ↓
5. VoiceGatewayService: Buffer transcripts until Eos
              ↓
6. VoiceGatewayService: Send complete transcript to frontend
              ↓
7. VoiceGatewayService: Pass transcript to C003 ExecuteAgentQueryUseCase
              ↓
8. C003 Agent: Process query → Response (with UI widgets)
              ↓
9. VoiceGatewayService: Route response to kyutai TTS WebSocket
              ↓
10. Kyutai TTS: Synthesize text → Audio messages (streaming)
               ↓
11. VoiceGatewayService: Stream audio chunks to frontend
               ↓
12. Frontend: Play audio (check for interrupt)
```

#### Conversational State Flow

```
1. User: "What's the weather?"
              ↓
2. STT: Transcript → VoiceGatewayService
              ↓
3. ConversationalState: Add message (role: "user", content: "What's the weather?")
              ↓
4. C003 Agent: Process query with context
              ↓
5. Agent: "The weather in San Francisco is 72°F."
              ↓
6. ConversationalState: Add message (role: "assistant", content: "...")
              ↓
7. TTS: Synthesize response
              ↓
8. User: "And in New York?"
              ↓
9. STT: Transcript → VoiceGatewayService
              ↓
10. ConversationalState: Add message (role: "user", content: "And in New York?")
              ↓
11. C003 Agent: See conversation history → "The weather in New York is 65°F."
              ↓
12. ConversationalState: Update context (topic: "weather", entities: ["San Francisco", "New York"])
```

---

## Migration Plan

### Phase 1: Coexistence (c004 + c010)

**Goal**: Implement c010 alongside c004, feature flag to switch

**Steps**:

1. Implement VoiceGatewayService and VoiceClient
2. Add feature flag: `USE_KYUTAI_EXTERNAL=true`
3. Update voice routes to support both modes
4. Add health check for kyutai server
5. Manual testing with both modes

**Validation**:
- [ ] VoiceGatewayService connects to kyutai
- [ ] STT → Agent → TTS flow works end-to-end
- [ ] Conversational state tracked correctly
- [ ] Feature flag switches between modes

### Phase 2: Deprecation (c004 marked deprecated)

**Goal**: Mark c004 internal services as deprecated

**Steps**:

1. Add deprecation notices to VADService, STTService, TTSService
2. Update docs to recommend c010
3. Set feature flag default: `USE_KYUTAI_EXTERNAL=true`
4. Monitor production usage

**Validation**:
- [ ] Deprecation warnings logged
- [ ] Production uses c010 by default
- [ ] No c004 usage for 7 days

### Phase 3: Removal (c004 removed)

**Goal**: Remove deprecated c004 code

**Steps**:

1. Remove VADService, STTService, TTSService classes
2. Remove internal model loading (torch, transformers, silero)
3. Remove feature flag (always use kyutai)
4. Update tests to mock kyutai server
5. Update dependencies (remove torch, transformers, silero)

**Validation**:
- [ ] All tests pass with kyutai mocks
- [ ] No deprecation warnings in logs
- [ ] Dependencies updated (torch removed)

### Rollback Strategy

**If c010 fails in production**:
1. Set feature flag: `USE_KYUTAI_EXTERNAL=false`
2. Restart AgentX services
3. System falls back to c004 internal services
4. Investigate c010 failure

**Rollback triggers**:
- Kyutai service unavailable >5 minutes
- Protocol mismatch errors >1% of requests
- Latency P95 >1000ms

---

## Open Questions

### Q1: Kyutai Server Deployment

**Question**: How to deploy kyutai voice-server in production?

**Options**:
- A. Docker container on same host as AgentX (simple, shared resources)
- B. Separate Docker container (isolated, independent scaling)
- C. Separate VM (full isolation, higher cost)

**Recommendation**: Option B (separate Docker container) with docker-compose

**Resolution**: Document in c010 tasks.md

### Q2: Session Persistence Storage

**Question**: Where to store conversation sessions?

**Options**:
- A. In-memory (simplest, lost on restart)
- B. Redis (fast, persists across restarts)
- C. Database (persistent, slower)

**Recommendation**: Option A (in-memory) for MVP, Option B (Redis) for production

**Resolution**: Implement in-memory first, add Redis in C005 (memory-rag)

### Q3: Concurrent Session Limits

**Question**: How many concurrent voice sessions to support?

**Options**:
- A. Unlimited (risk resource exhaustion)
- B. Fixed limit (5 sessions)
- C. Dynamic limit based on resources

**Recommendation**: Option B (5 sessions) for MVP

**Resolution**: Add configurable limit in VoiceGatewayService

### Q4: Error Recovery Strategy

**Question**: What to do when kyutai returns an error?

**Options**:
- A. Retry immediately (may overwhelm kyutai)
- B. Retry with exponential backoff (recommended)
- C. Fail fast to text mode

**Recommendation**: Option B (retry 3x with backoff) → Option C (text mode)

**Resolution**: Implement retry logic in VoiceGatewayService

---

**Next Artifact**: specs/**/*.md
