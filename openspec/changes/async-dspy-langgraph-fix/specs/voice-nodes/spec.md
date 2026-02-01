# Spec: Voice Nodes

**Domain**: agent-runtime
**Generated**: 2026-02-02
**Status**: Draft

---

## 1. Purpose

Define the voice session nodes for the voice subgraph (excluding cleanup).

**Success Criteria**:
- 7 nodes for voice session flow
- Each node updates VoiceState
- All nodes route to cleanup eventually
- Error handling in each node

---

## 2. Scope

### In Scope

- connect_kyutai_node
- listen_audio_node
- transcribe_node
- process_agent_node
- synthesize_node
- stream_audio_node
- check_interrupt_node

### Out of Scope

- Cleanup node (covered by voice-cleanup spec)
- VoiceState model (covered by voice-state spec)

---

## 3. Requirements

### 3.1 Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-VN-001 | connect_kyutai MUST connect STT and TTS | Must |
| FR-VN-002 | listen_audio MUST use VAD | Should |
| FR-VN-003 | transcribe MUST call STT service | Must |
| FR-VN-004 | process_agent MUST invoke main graph | Must |
| FR-VN-005 | synthesize MUST check interrupt | Should |
| FR-VN-006 | check_interrupt MUST route to cleanup on interrupt | Must |

---

## 4. API Contract

```python
# agent/nodes/voice/voice_nodes.py

async def connect_kyutai_node(state: VoiceState) -> dict:
    """Connect to Kyutai STT and TTS WebSocket servers."""
    session_id = state["session_id"]

    stt_connected = await voice_gateway.connect_stt(session_id)
    tts_connected = await voice_gateway.connect_tts(session_id)

    if not stt_connected or not tts_connected:
        return {
            "error_message": "Failed to connect to Kyutai servers",
            "should_terminate": True,
            "current_step": "cleanup",
        }

    return {
        "stt_connected": True,
        "tts_connected": True,
        "current_step": "listen_audio",
    }

async def listen_audio_node(state: VoiceState) -> dict:
    """Listen for audio input from frontend (with VAD)."""
    # Receive audio chunk
    audio_chunk = await frontend_ws.receive_bytes()

    # Apply VAD
    has_speech = await vad_service.detect_speech(audio_chunk)

    if has_speech:
        return {
            "audio_input_buffer": [audio_chunk],
            "current_step": "transcribe",
        }

    return {"current_step": "listen_audio"}

async def transcribe_node(state: VoiceState) -> dict:
    """Transcribe audio to text using Kyutai STT."""
    audio_buffer = state.get("audio_input_buffer", [])
    transcribed = await stt_service.transcribe(audio_buffer)

    return {
        "transcribed_text": transcribed,
        "current_step": "process_agent",
        "audio_input_buffer": [],
    }

async def process_agent_node(state: VoiceState) -> dict:
    """Process transcribed text through agent (main graph invocation)."""
    transcribed = state.get("transcribed_text", "")

    # Invoke main agent graph
    result = await main_agent_graph.ainvoke(
        {"query": transcribed, "input_path": InputPath.TEXT},
        config={"configurable": {"thread_id": state["session_id"]}},
    )

    return {
        "agent_response": result.get("final_response", ""),
        "synthesis_pending": True,
        "current_step": "synthesize",
    }

async def synthesize_node(state: VoiceState) -> dict:
    """Synthesize agent response to audio using Kyutai TTS."""
    response = state.get("agent_response", "")
    audio_chunks = []

    async for chunk in tts_service.synthesize_stream(response):
        if state.get("synthesis_interrupted", False):
            break  # User interrupted
        audio_chunks.append(chunk)

    return {
        "audio_output_buffer": audio_chunks,
        "synthesis_pending": False,
        "current_step": "stream_audio",
    }

async def stream_audio_node(state: VoiceState) -> dict:
    """Stream audio output to frontend."""
    audio_buffer = state.get("audio_output_buffer", [])

    for chunk in audio_buffer:
        await frontend_ws.send_bytes(chunk)

    return {
        "audio_output_buffer": [],
        "current_step": "check_interrupt",
    }

async def check_interrupt_node(state: VoiceState) -> dict:
    """Check if user interrupted or session should continue."""
    # Check for interrupt signal
    interrupt = await frontend_ws.receive_json()

    if interrupt.get("type") == "interrupt":
        return {
            "synthesis_interrupted": True,
            "current_step": "cleanup",
        }

    # Continue listening
    return {
        "synthesis_interrupted": False,
        "current_step": "listen_audio",
    }
```

---

## 5. Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-VN-001 | Connection error → cleanup | should_terminate=True |
| BR-VN-002 | User interrupt → cleanup | synthesis_interrupted=True |
| BR-VN-003 | Audio buffers cleared after use | Empty list return |

---

## 6. Acceptance Criteria

- [ ] All 7 nodes implemented
- [ ] Each node returns dict with state updates
- [ ] Error paths route to cleanup
- [ ] Interrupt detection works
- [ ] Ruff and pyrefly checks pass

---

## 7. Node Flow

```
connect_kyutai → listen_audio → transcribe → process_agent
    → synthesize → stream_audio → check_interrupt
        ↘ (interrupt) cleanup
        ↘ (continue) listen_audio
```

---

**Next**: See `voice-cleanup/spec.md` for cleanup node implementation.
