# Spec: voice-client

**File**: `specs/voice-client/spec.md`

**Generated**: 2026-01-31
**Change**: c010-voice-client

---

## 1.1 Purpose

Define the voice client infrastructure for connecting to external kyutai voice-server from the frontend. This spec covers WebSocket connection management, message routing, and reconnection logic.

---

## 1.2 Scope

**In Scope**:
- VoiceClient class for frontend WebSocket connection
- Message routing (STT, TTS, Error)
- Reconnection logic with exponential backoff
- Graceful degradation when kyutai unavailable

**Out of Scope**:
- Audio recording (handled by browser MediaRecorder)
- Audio playback (handled by browser Audio API)
- Conversation UI (covered by conversational-state spec)

---

## 1.3 Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-VC-001 | VoiceClient MUST establish single WebSocket connection to AgentX on port 8019 | Must |
| FR-VC-002 | VoiceClient MUST send Audio messages with base64-encoded audio chunks | Must |
| FR-VC-003 | VoiceClient MUST receive Text messages (transcripts) and stream to UI | Must |
| FR-VC-004 | VoiceClient MUST receive Audio messages (TTS) and play via Audio API | Must |
| FR-VC-005 | VoiceClient MUST handle Error messages and display to user | Must |
| FR-VC-006 | VoiceClient MUST automatically reconnect with exponential backoff on disconnect | Must |
| FR-VC-007 | VoiceClient MUST support interruption via Interrupt message | Must |
| FR-VC-008 | VoiceClient MUST degrade gracefully when kyutai unavailable | Must |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-VC-001 | VoiceClient MUST use TypeScript with strict type checking | Must |
| NFR-VC-002 | VoiceClient MUST pass ESLint check with no warnings | Must |
| NFR-VC-003 | VoiceClient MUST handle WebSocket messages within 50ms | Should |
| NFR-VC-004 | VoiceClient MUST support concurrent connections (max 5 sessions) | Must |

---

## 1.4 Data Model

### File: frontend/lib/voice/client.ts

```typescript
import { v4 as uuidv4 } from "uuid";
import { VoiceMessage, VoiceMessageType, VoiceProtocol } from "./types";

export interface VoiceClientConfig {
  url: string; // ws://localhost:8019/ws/voice
  session_id?: string;
  reconnect_interval?: number; // Default: 1000ms
  max_reconnect_attempts?: number; // Default: 10
}

export interface VoiceClientState {
  connected: boolean;
  reconnecting: boolean;
  reconnect_attempts: number;
  last_error: string | null;
}

export class VoiceClient {
  private ws: WebSocket | null = null;
  private config: VoiceClientConfig;
  private state: VoiceClientState;
  private message_handlers: Map<VoiceMessageType, (msg: VoiceMessage) => void>;

  constructor(config: VoiceClientConfig) {
    this.config = {
      ...config,
      session_id: config.session_id || uuidv4(),
      reconnect_interval: config.reconnect_interval || 1000,
      max_reconnect_attempts: config.max_reconnect_attempts || 10,
    };
    this.state = {
      connected: false,
      reconnecting: false,
      reconnect_attempts: 0,
      last_error: null,
    };
    this.message_handlers = new Map();
  }

  connect(): void {
    const url = `${this.config.url}?session_id=${this.config.session_id}`;
    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      this.state.connected = true;
      this.state.reconnecting = false;
      this.state.reconnect_attempts = 0;
      this.state.last_error = null;
      console.log("[VoiceClient] Connected");
    };

    this.ws.onmessage = (event) => {
      const message: VoiceMessage = JSON.parse(event.data);
      this.handle_message(message);
    };

    this.ws.onclose = () => {
      this.state.connected = false;
      if (!this.state.reconnecting && this.state.reconnect_attempts < this.config.max_reconnect_attempts!) {
        this.reconnect();
      }
    };

    this.ws.onerror = (error) => {
      this.state.last_error = "WebSocket error";
      console.error("[VoiceClient] Error:", error);
    };
  }

  private reconnect(): void {
    this.state.reconnecting = true;
    this.state.reconnect_attempts++;
    const delay = this.config.reconnect_interval! * Math.pow(2, this.state.reconnect_attempts - 1);
    console.log(`[VoiceClient] Reconnecting in ${delay}ms (attempt ${this.state.reconnect_attempts})`);
    setTimeout(() => this.connect(), delay);
  }

  private handle_message(message: VoiceMessage): void {
    const handler = this.message_handlers.get(message.type);
    if (handler) {
      handler(message);
    }
  }

  send_audio(audio_base64: string): void {
    const message: VoiceMessage = {
      type: VoiceMessageType.AUDIO,
      data: audio_base64,
      session_id: this.config.session_id!,
      timestamp: Date.now() / 1000,
    };
    this.send(message);
  }

  send_interrupt(): void {
    const message: VoiceMessage = {
      type: VoiceMessageType.INTERRUPT,
      data: "interrupt",
      session_id: this.config.session_id!,
      timestamp: Date.now() / 1000,
    };
    this.send(message);
  }

  on(message_type: VoiceMessageType, handler: (msg: VoiceMessage) => void): void {
    this.message_handlers.set(message_type, handler);
  }

  private send(message: VoiceMessage): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    }
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.state.connected = false;
    this.state.reconnecting = false;
  }

  get_state(): VoiceClientState {
    return { ...this.state };
  }
}
```

---

## 1.5 Acceptance Criteria

- [ ] VoiceClient connects to AgentX WebSocket on port 8019
- [ ] VoiceClient sends Audio messages with base64-encoded audio
- [ ] VoiceClient receives and routes Text messages to registered handlers
- [ ] VoiceClient receives and plays Audio messages via Audio API
- [ ] VoiceClient automatically reconnects with exponential backoff
- [ ] VoiceClient degrades gracefully when kyutai unavailable
- [ ] VoiceClient supports interruption via Interrupt message
- [ ] VoiceClient passes TypeScript strict type checking
- [ ] VoiceClient passes ESLint check with no warnings

---

**Related Specs**:
- `voice-gateway` - Backend service for routing messages
- `conversational-state` - Conversation state management
- `voice-stream-handling` - Text stream processing

---
