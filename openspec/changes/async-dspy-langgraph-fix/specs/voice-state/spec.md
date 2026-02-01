# Spec: Voice State Model

**Domain**: agent-runtime
**Generated**: 2026-02-02
**Status**: Draft

---

## 1. Purpose

Define the VoiceState TypedDict for managing voice session state in the voice subgraph.

**Success Criteria**:
- VoiceState TypedDict defined
- Session identifiers included
- Connection state tracked
- Audio buffers managed

---

## 2. Scope

### In Scope

- VoiceState TypedDict definition
- Session state fields
- Connection status fields
- Audio buffer fields

### Out of Scope

- Voice nodes implementation (covered by voice-nodes spec)
- Cleanup guarantee (covered by voice-cleanup spec)

---

## 3. Requirements

### 3.1 Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-VS-001 | VoiceState MUST include session_id | Must |
| FR-VS-002 | VoiceState MUST track WebSocket connections | Must |
| FR-VS-003 | VoiceState MUST include audio buffers | Must |
| FR-VS-004 | VoiceState MUST track current step | Should |

---

## 4. Data Model

```python
# domain/models/voice_state.py
from typing import TypedDict, Literal

class VoiceState(TypedDict):
    """Voice session state for TTS/STT subgraph."""

    # Session identifiers
    session_id: str
    user_id: str

    # WebSocket connections (managed outside state)
    stt_connected: bool
    tts_connected: bool
    frontend_connected: bool

    # Audio streams
    audio_input_buffer: list[bytes]
    audio_output_buffer: list[bytes]

    # Transcription and synthesis
    transcribed_text: str
    synthesis_pending: bool
    synthesis_interrupted: bool

    # Agent communication
    agent_response: str

    # Status tracking
    current_step: Literal[
        "connect_kyutai",
        "listen_audio",
        "transcribe",
        "process_agent",
        "synthesize",
        "stream_audio",
        "check_interrupt",
        "cleanup",
    ]

    # Error handling
    error_message: str | None
    should_terminate: bool
```

---

## 5. Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| session_id | str | Unique voice session identifier |
| user_id | str | User ID for session association |
| stt_connected | bool | STT WebSocket connection status |
| tts_connected | bool | TTS WebSocket connection status |
| frontend_connected | bool | Frontend WebSocket connection status |
| audio_input_buffer | list[bytes] | Incoming audio chunks from user |
| audio_output_buffer | list[bytes] | Outgoing audio chunks to user |
| transcribed_text | str | Text transcribed from audio |
| synthesis_pending | bool | Whether TTS synthesis is pending |
| synthesis_interrupted | bool | Whether user interrupted synthesis |
| agent_response | str | Agent's response to synthesize |
| current_step | Literal | Current node in voice subgraph |
| error_message | str \| None | Error message if any |
| should_terminate | bool | Whether session should terminate |

---

## 6. Business Rules

| Rule | Description |
|------|-------------|
| BR-VS-001 | Only one audio operation at a time |
| BR-VS-002 | Buffers cleared after each operation |
| BR-VS-003 | current_step always reflects actual node |

---

## 7. Acceptance Criteria

- [ ] VoiceState TypedDict created
- [ ] All required fields defined
- [ ] Literal type for current_step
- [ ] Optional fields marked with |
| [ ] Pyrefly type checking passes

---

## 8. Usage Example

```python
# Initialize voice state
voice_state: VoiceState = {
    "session_id": "voice_12345",
    "user_id": "user_abc",
    "stt_connected": False,
    "tts_connected": False,
    "frontend_connected": True,
    "audio_input_buffer": [],
    "audio_output_buffer": [],
    "transcribed_text": "",
    "synthesis_pending": False,
    "synthesis_interrupted": False,
    "agent_response": "",
    "current_step": "connect_kyutai",
    "error_message": None,
    "should_terminate": False,
}

# Update after connection
voice_state.update({
    "stt_connected": True,
    "tts_connected": True,
    "current_step": "listen_audio",
})
```

---

**Next**: See `voice-nodes/spec.md` for voice node implementations.
