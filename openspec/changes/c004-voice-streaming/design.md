# Design Artifact: c004-voice-streaming

**Generated**: 2026-01-28
**Change**: c004-voice-streaming
**Schema**: spec-factory v1

---

## 1. Architecture

### 1.1 Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Voice Streaming System                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Frontend (Browser/Mobile)                                              │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Voice Client (WebSocket)                                        │  │
│  │    - Capture audio (any sample rate)                             │  │
│  │    - Send AUDIO_CHUNK messages                                   │  │
│  │    - Receive/play RESPONSE_AUDIO messages                        │  │
│  │    - Send INTERRUPT on user action                               │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                              ↕ WebSocket (port 8019)                   │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Voice Routes (FastAPI)                                          │  │
│  │    - POST /api/v1/voice/session (port 8018)                      │  │
│  │    - WebSocket /ws/voice                                          │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                              ↓                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  VoicePipelineUseCase (Application Layer)                        │  │
│  │    ┌────────────────────────────────────────────────────────┐    │  │
│  │    │  Full Duplex WebSocket Handler                         │    │  │
│  │    │    - input_task: Receive AUDIO_CHUNK                    │    │  │
│  │    │    - output_task: Send RESPONSE_AUDIO                   │    │  │
│  │    │    - Interrupt handling                                 │    │  │
│  │    └────────────────────────────────────────────────────────┘    │  │
│  │                                                                 │  │
│  │    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐ │  │
│  │    │   VAD    │───▶│   STT    │───▶│   LLM    │───▶│   TTS    │ │  │
│  │    │ Service  │    │ Service  │    │ (C003)   │    │ Service  │ │  │
│  │    └──────────┘    └──────────┘    └──────────┘    └──────────┘ │  │
│  │         ↓              ↓               ↓               ↓          │  │
│  │    Filter silence   Transcribe    Process text   Stream audio   │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                              ↓                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Voice Services (Infrastructure Layer)                           │  │
│  │    - VADService (Silero VAD, 16kHz)                              │  │
│  │    - STTService (Kyutai STT 2.6B, 16kHz)                         │  │
│  │    - TTSService (Pocket TTS, 24kHz, streaming)                   │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Layer Structure (Clean Architecture)

```
agentx/
├── core/                           # Configuration
│   └── config.py                   # Voice service settings
├── domain/                         # Business entities
│   └── entities/
│       └── voice_session.py        # VoiceSessionEntity (@dataclass)
├── application/                    # Use case orchestration
│   ├── use_cases/
│   │   └── voice_pipeline_use_case.py
│   └── dtos/
│       └── voice_dtos.py           # AudioChunkMessage, TranscriptMessage, etc.
├── infrastructure/                 # External services
│   └── external/
│       ├── vad_service.py          # VADService (Silero VAD)
│       ├── stt_service.py          # STTService (Kyutai STT 2.6B)
│       └── tts_service.py          # TTSService (Pocket TTS)
└── presentation/                   # FastAPI routes
    └── api/
        └── v1/
            └── voice_routes.py     # REST + WebSocket endpoints
```

### 1.3 WebSocket Full Duplex Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Full Duplex WebSocket Flow                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Client                                                 Server         │
│    │                                                     │             │
│    │ ┌───────────────────────────────────────────────┐  │             │
│    │ │         Input Task (Client → Server)           │  │             │
│    │ │  AUDIO_CHUNK ──▶ VAD ──▶ STT ──▶ LLM          │  │             │
│    │ └───────────────────────────────────────────────┘  │             │
│    │                                                     │             │
│    │ ┌───────────────────────────────────────────────┐  │             │
│    │ │         Output Task (Server → Client)          │  │             │
│    │ │         TTS ──▶ RESPONSE_CHUNK ──▶ Play        │  │             │
│    │ │             (check interrupt flag)             │  │             │
│    │ └───────────────────────────────────────────────┘  │             │
│    │                                                     │             │
│    │ ┌───────────────────────────────────────────────┐  │             │
│    │ │         Interrupt (Client → Server)            │  │             │
│    │ │  INTERRUPT ──▶ Set flag ──▶ Stop TTS           │  │             │
│    │ └───────────────────────────────────────────────┘  │             │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Data Flow

### 2.1 Voice Request Flow (Speech → Speech)

```
1. Client sends AUDIO_CHUNK (any sample rate)
              ↓
2. WebSocket input_task receives audio
              ↓
3. VADService detects speech probability
              ↓
4. If speech: STTService transcribes to text
              ↓
5. ExecuteAgentQueryUseCase (C003) processes text → LLM response
              ↓
6. TTSService streams audio in chunks
              ↓
7. WebSocket output_task sends RESPONSE_AUDIO chunks
              ↓
8. Client plays audio (checks for INTERRUPT)
```

### 2.2 Interruption Flow

```
1. User presses "Stop" button
              ↓
2. Client sends INTERRUPT message
              ↓
3. Server sets session.interrupted = True
              ↓
4. TTSService.astream_synthesize() checks flag in loop
              ↓
5. TTS generation stops immediately
              ↓
6. Server sends RESPONSE_AUDIO with is_interrupted=True
              ↓
7. Client stops playback, returns to LISTENING state
```

### 2.3 Session Lifecycle

```
CREATED ──▶ LISTENING ──▶ PROCESSING ──▶ SPEAKING ──▶ LISTENING
   │            │              │             │
   │            ▼              ▼             │
   │         (idle)        (STT→LLM)     (TTS)
   │                                          │
   └──────────────────────────────────────────┘
                      │
                      ▼
                  CLOSED
          (timeout, disconnect, error)
```

---

## 3. Technical Decisions

| Decision | Option Chosen | Alternatives | Rationale |
|----------|---------------|--------------|-----------|
| **VAD Model** | Silero VAD | WebRTC VAD, Custom model | <50ms latency, high accuracy, CPU-only |
| **STT Model** | Kyutai STT 2.6B | Whisper, AssemblyAI | Streaming support, English optimized, free |
| **TTS Model** | Pocket TTS (100M) | Silero TTS, ElevenLabs | Low latency, good quality, free |
| **Chunk Size** | 500ms | 250ms, 1s | Balances latency vs message overhead |
| **Duplex Mode** | Full duplex (separate tasks) | Half-duplex (turn-based) | Required for interruption, natural feel |
| **Memory Strategy** | Reload every 100 calls | Process isolation, Caching | Simple, effective, low overhead |
| **Sample Rates** | 16kHz in, 24kHz out | All 16kHz, all 48kHz | Matches model requirements, good quality |
| **Ports** | 8018-8020 | 8000-8014, 8080 | Avoids conflicts (C003 uses port 2024) |
| **Voice UI** | LangGraph server-driven UI | Custom WebSocket UI | Industry standard, state sync via ui_message_reducer |
| **Voice Visual** | 2D SVG metaballs (nucleus) | 3D WebGL, Canvas | Cheap goo filters, platform-aware (16/12px blur) |
| **Interrupt Button** | Server-driven UI component | Custom button | Google Assistant reference, Shadow DOM isolation |

---

## 4. Tradeoff Analysis

### 4.1 Approach A: Turn-Based (Half Duplex)

| Aspect | Rating | Notes |
|--------|--------|-------|
| Simplicity | ⭐⭐⭐ | Single task, sequential |
| Latency | ⭐⭐ | 500-1000ms (wait for full speech) |
| Natural Feel | ⭐ | Can't interrupt, feels robotic |

**Pros**:
- Simple implementation
- Easier testing
- Less state management

**Cons**:
- Cannot interrupt during TTS
- Higher latency (wait for full speech)
- Unnatural conversation flow

### 4.2 Approach B: Streaming Full Duplex (Chosen)

| Aspect | Rating | Notes |
|--------|--------|-------|
| Simplicity | ⭐⭐ | Separate tasks, concurrent state |
| Latency | ⭐⭐⭐ | <300ms (streaming) |
| Natural Feel | ⭐⭐⭐ | Can interrupt, real-time feel |

**Pros**:
- Low latency (streaming)
- Interruption support
- Natural conversation flow

**Cons**:
- More complex (concurrent tasks)
- Race condition handling
- More state to manage

### 4.3 Decision: Streaming Full Duplex

**Rationale**: Voice interface requires interruption for natural interaction. The added complexity is justified by significantly better UX. Prototype R011 validated this pattern successfully.

---

## 5. Implementation Details

### 5.1 Key Classes/Modules

| Module | Responsibility | Dependencies |
|--------|----------------|--------------|
| **VoiceSessionEntity** | Track session state, transcript, interruption flag | domain.entities |
| **VADService** | Detect speech probability, filter silence | torch, silero_vad |
| **STTService** | Transcribe audio to text | transformers, torch |
| **TTSService** | Synthesize text to audio, streaming | transformers, torch |
| **VoicePipelineUseCase** | Orchestrate VAD → STT → LLM → TTS flow | All services + C003 |
| **WebSocket handler** | Full duplex input/output tasks | WebSocketManager (C002) |

### 5.2 Port Assignments

| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| LangGraph Server (C003) | 2024 | HTTP | Server-driven UI, agent execution |
| Voice API | 8018 | HTTP | REST endpoints (session management) |
| Voice WebSocket | 8019 | WS | Full duplex audio streaming |
| Voice Health | 8020 | HTTP | Health check endpoint |

**Note**: C003-agent-pipeline uses LangGraph server on port 2024 (updated from 8015-8017).

### 5.3 Storage Schema

```python
# Voice sessions are transient (in-memory)
# No database persistence required for voice sessions

@dataclass
class VoiceSessionEntity:
    session_id: UUID
    state: VoiceSessionState
    created_at: datetime
    last_activity_at: datetime
    interrupted: bool = False
    audio_chunks_received: int = 0
    transcript: Optional[str] = None
    llm_response: Optional[str] = None
```

### 5.4 File Structure

```
agentx/
├── domain/entities/
│   └── voice_session.py           # VoiceSessionEntity (100 lines max)
├── application/use_cases/
│   └── voice_pipeline_use_case.py  # VoicePipelineUseCase (100 lines max)
├── application/dtos/
│   └── voice_dtos.py               # Pydantic DTOs (100 lines max)
├── infrastructure/external/
│   ├── vad_service.py              # VADService (100 lines max)
│   ├── stt_service.py              # STTService (100 lines max)
│   └── tts_service.py              # TTSService (100 lines max)
└── presentation/api/v1/
    └── voice_routes.py             # REST + WebSocket (100 lines max)
```

---

## 6. Security Considerations

| Concern | Mitigation |
|---------|------------|
| **WebSocket hijacking** | Session ID validation, origin header check |
| **Audio injection** | Rate limiting per session, max chunk size |
| **DoS (large audio)** | Max session duration (5 min), max concurrent sessions (5) |
| **Memory exhaustion** | TTS model reload, session timeout cleanup |
| **Privacy (audio data)** | No audio logging, ephemeral sessions only |

---

## 7. Performance Considerations

| Concern | Mitigation |
|---------|------------|
| **Latency** | Streaming pipeline, VAD filtering, 500ms chunks |
| **Memory leaks** | TTS model reload every 100 generations |
| **Concurrent sessions** | Limit to 5 sessions, monitor resources |
| **Audio resampling** | Use torchaudio.transforms.Resample (GPU accelerated) |
| **Model loading** | Load on startup, health check waits for ready |
| **Interruption lag** | Check flag every chunk (every 500ms) |

### 7.1 Latency Budget

| Component | Target | Notes |
|-----------|--------|-------|
| VAD | <50ms | Silero VAD on CPU |
| STT | <200ms | Kyutai STT 2.6B |
| LLM (C003) | <300ms | Ollama gemma3:4b |
| TTS | <100ms | Pocket TTS first chunk |
| **Total** | <500ms | P95 target, P50 <300ms |

### 7.2 Resource Requirements

| Resource | Expected | Max |
|----------|----------|-----|
| Memory (VAD) | ~50MB | 100MB |
| Memory (STT) | ~5GB | 6GB |
| Memory (TTS) | ~2GB (with reload) | 3GB |
| GPU (optional) | 2GB VRAM | 4GB VRAM |
| CPU (no GPU) | 50% per session | 100% |

---

## 8. Integration Points

### 8.1 C002 Data Contracts

```python
from ui.protocols.websocket_messages import WebSocketMessageType

# Message types used:
# - AUDIO_CHUNK (client → server)
# - TRANSCRIPT (server → client)
# - RESPONSE_AUDIO (server → client)
# - INTERRUPT (client → server)
# - SESSION_START (server → client)
# - SESSION_END (server → client)
```

### 8.2 C003 Agent Pipeline

```python
from application.use_cases.execute_agent_query import ExecuteAgentQueryUseCase
from application.dtos.agent_dtos import ExecuteAgentQueryCommand, ExecuteAgentQueryResponse

# Integration point:
use_case = get_execute_agent_query_use_case()
command = ExecuteAgentQueryCommand(session_id=session_id, query=transcript)
response = await use_case.execute(command)
llm_response = response.answer  # Pass to TTS
```

### 8.3 C007 Frontend Architecture (LangGraph Server-Driven UI)

**Voice UI Integration with LangGraph**:

Voice pipeline integrates with LangGraph server-driven UI architecture to provide visual feedback during voice interactions. Voice state changes emit UI messages via `push_ui_message()`.

```python
# File: application/use_cases/voice_pipeline_use_case.py
from langgraph.graph.ui import push_ui_message, AnyUIMessage

class VoicePipelineUseCase:
    async def update_voice_state(self, session_id: UUID, state: VoiceSessionState):
        """Emit voice state UI update via LangGraph."""
        if state == VoiceSessionState.LISTENING:
            push_ui_message(
                "voiceStatus",
                {
                    "state": "listening",
                    "icon": "mic",
                    "pulse": True,  # Animate for voice nucleus
                },
                message=None  # Standalone UI update
            )
        elif state == VoiceSessionState.PROCESSING:
            push_ui_message(
                "voiceStatus",
                {
                    "state": "processing",
                    "icon": "brain",
                    "pulse": False,
                },
                message=None
            )
        elif state == VoiceSessionState.SPEAKING:
            push_ui_message(
                "voiceStatus",
                {
                    "state": "speaking",
                    "icon": "speaker",
                    "pulse": True,
                },
                message=None
            )
```

**Voice Nucleus Widget** (from C008 Organic UI):

The voice nucleus widget provides bio-inspired visual feedback during voice interactions.

```typescript
// File: src/agent/ui.tsx (colocated with graph.py)
import { VoiceNucleusWidget } from "./widgets/VoiceNucleusWidget";

export default {
  // ... existing widget exports
  voiceStatus: VoiceNucleusWidget,
};
```

```typescript
// File: src/agent/widgets/VoiceNucleusWidget.tsx
interface VoiceStatusProps {
  state: "listening" | "processing" | "speaking";
  icon: string;
  pulse: boolean;
}

export function VoiceNucleusWidget(props: VoiceStatusProps) {
  const size = props.state === "speaking" ? "160px" : "72px"; // Desktop vs mobile

  return (
    <div className={`voice-nucleus ${props.state} ${props.pulse ? "pulse" : ""}`}>
      <div className="nucleus-core" style={{ width: size, height: size }}>
        <svg className={`icon-${props.icon}`}>
          {/* Bio-inspired SVG icon */}
        </svg>
      </div>
      {/* Metaball effects (2D SVG filters) */}
    </div>
  );
}
```

**Interrupt Button Pattern** (Google Assistant reference):

Voice interruption uses a server-driven UI button component.

```python
# Backend: Emit interrupt button when speaking starts
push_ui_message(
    "interruptButton",
    {
        "label": "Stop",
        "action": "interrupt_voice",
        "variant": "destructive",  // Red outline button
    },
    message=message
)
```

```typescript
// Frontend: LoadExternalComponent renders button
// Click sends INTERRUPT message to WebSocket
function onInterruptClick() {
    websocket.send(JSON.stringify({
        type: "INTERRUPT",
        data: { interrupted: true }
    }));
}
```

**Design Tokens** (from C008 Organic UI):

```typescript
// File: frontend/design/tokens.ts
export const voiceTokens = {
  nucleus: {
    sizeDesktop: 160,    // px
    sizeMobile: 72,      // px
    blurDesktop: 16,     // px
    blurMobile: 12,      // px
    maxBlobsMobile: 6,   // Mobile optimization
  },
  colors: {
    void: '#0A0A0A',
    membrane: '#141414',
    enzyme: '#00D9FF',   // Cyan accent for voice
  },
};
```

**Frontend Integration Pattern**:

```tsx
// File: frontend/app/voice/page.tsx
import { useStream } from "@langchain/langgraph-sdk/react";
import { LoadExternalComponent } from "@langchain/langgraph-sdk/react-ui";

function VoicePage() {
  const { thread, values } = useStream({
    apiUrl: "http://localhost:2024",
    assistantId: "agent",
    onCustomEvent: (event, options) => {
      options.mutate((prev) => {
        const ui = uiMessageReducer(prev.ui ?? [], event);
        return { ...prev, ui };
      });
    },
  });

  return (
    <div>
      {/* Voice nucleus widget from server */}
      {values.ui?.filter(u => u.name === "voiceStatus").map((ui) => (
        <LoadExternalComponent
          key={ui.id}
          stream={thread}
          message={ui}
          fallback={<VoiceSkeleton />}
        />
      ))}
    </div>
  );
}
```

---

**Next Artifact**: tasks.md
