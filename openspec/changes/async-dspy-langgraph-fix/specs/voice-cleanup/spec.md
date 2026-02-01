# Spec: Voice Cleanup Guarantee

**Domain**: agent-runtime
**Generated**: 2026-02-02
**Status**: Draft

---

## 1. Purpose

Define the cleanup node pattern that guarantees WebSocket cleanup for voice sessions.

**Problem**: Current C010 implementation uses `asyncio.gather()` which doesn't guarantee cleanup on errors.

**Success Criteria**:
- ALL execution paths lead to cleanup node
- Cleanup closes STT WebSocket
- Cleanup closes TTS WebSocket
- Cleanup clears session state

---

## 2. Scope

### In Scope

- cleanup_node implementation
- WebSocket closing logic
- Session state clearing
- Graph wiring for ALL paths to cleanup

### Out of Scope

- Voice session flow (covered by voice-nodes spec)
- Voice state model (covered by voice-state spec)

---

## 3. Requirements

### 3.1 Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-VC-001 | cleanup_node MUST close STT WebSocket | Must |
| FR-VC-002 | cleanup_node MUST close TTS WebSocket | Must |
| FR-VC-003 | cleanup_node MUST clear session state | Must |
| FR-VC-004 | ALL graph paths MUST lead to cleanup | Must |
| FR-VC-005 | Cleanup MUST run even on errors | Must |

### 3.2 Non-Functional Requirements

| ID | Requirement | Target Metric |
|----|-------------|---------------|
| NFR-VC-001 | Cleanup latency | < 1s |

---

## 4. Data Model

```python
# Using VoiceState from voice-state spec
from domain.models.voice_state import VoiceState
```

---

## 5. API Contract

```python
# agent/nodes/voice/voice_nodes.py

async def cleanup_node(state: VoiceState) -> dict:
    """CLEANUP NODE: Always runs, even on errors.

    CRITICAL: This node MUST run to prevent WebSocket leaks.
    This is the FINAL node in the voice subgraph - ALL paths lead here.

    Args:
        state: Current voice state

    Returns:
        dict: Reset state with all connections closed
    """
    session_id = state["session_id"]

    # Close STT WebSocket
    if state.get("stt_connected"):
        try:
            await voice_gateway.disconnect_stt(session_id)
        except Exception as e:
            logger.error(f"STT disconnect error: {e}")

    # Close TTS WebSocket
    if state.get("tts_connected"):
        try:
            await voice_gateway.disconnect_tts(session_id)
        except Exception as e:
            logger.error(f"TTS disconnect error: {e}")

    # Clear session state
    await text_handler.clear_session(session_id)

    # Return reset state
    return {
        "stt_connected": False,
        "tts_connected": False,
        "frontend_connected": False,
        "audio_input_buffer": [],
        "audio_output_buffer": [],
        "transcribed_text": "",
        "synthesis_pending": False,
        "synthesis_interrupted": False,
        "current_step": "cleanup",
        "error_message": None,
        "should_terminate": True,  # Ensure termination
    }
```

---

## 6. Graph Wiring

```python
# agent/nodes/voice/voice_subgraph.py

def build_voice_subgraph() -> StateGraph:
    """Build voice subgraph with GUARANTEED cleanup."""

    builder = StateGraph(VoiceState)

    # Add nodes (including cleanup)
    builder.add_node("connect_kyutai", connect_kyutai_node)
    builder.add_node("listen_audio", listen_audio_node)
    builder.add_node("transcribe", transcribe_node)
    builder.add_node("synthesize", synthesize_node)
    builder.add_node("check_interrupt", check_interrupt_node)
    builder.add_node("cleanup", cleanup_node)  # ← CRITICAL NODE

    # Entry point
    builder.add_edge(START, "connect_kyutai")

    # ALL conditional edges lead to cleanup (guaranteed!)
    builder.add_conditional_edges(
        "connect_kyutai",
        lambda s: "cleanup" if s.get("should_terminate") else "listen_audio",
        {
            "cleanup": "cleanup",  # Error path → cleanup
            "listen_audio": "listen_audio",  # Success path
        }
    )

    builder.add_edge("listen_audio", "transcribe")
    builder.add_edge("transcribe", "synthesize")
    builder.add_edge("synthesize", "check_interrupt")

    # After interrupt check: either continue or cleanup
    builder.add_conditional_edges(
        "check_interrupt",
        lambda s: "cleanup" if s.get("synthesis_interrupted") else "listen_audio",
        {
            "cleanup": "cleanup",  # Interrupt → cleanup
            "listen_audio": "listen_audio",  # Continue listening
        }
    )

    # FINAL EDGE: cleanup → END (guaranteed termination)
    builder.add_edge("cleanup", END)

    return builder.compile()
```

---

## 7. Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-VC-001 | Cleanup on error | should_terminate routes to cleanup |
| BR-VC-002 | Cleanup on interrupt | synthesis_interrupted routes to cleanup |
| BR-VC-003 | Cleanup on completion | Normal flow → check_interrupt → cleanup |
| BR-VC-004 | No bypass paths | All edges verified to lead to cleanup |

---

## 8. Acceptance Criteria

- [ ] cleanup_node closes STT WebSocket
- [ ] cleanup_node closes TTS WebSocket
- [ ] cleanup_node clears session state
- [ ] ALL conditional edges lead to cleanup
- [ ] Cleanup → END edge exists
- [ ] Cleanup runs even on errors (try/except)
- [ ] Ruff and pyrefly checks pass

---

## 9. Test Scenarios

| Scenario | Expected Behavior |
|----------|------------------|
| Normal completion | Flow → check_interrupt → cleanup → END |
| User interrupt | Interrupt detected → cleanup → END |
| Connection error | should_terminate → cleanup → END |
| STT WebSocket error | Exception caught, cleanup continues |
| TTS WebSocket error | Exception caught, cleanup continues |

---

## 10. Verification

```bash
# Verify ALL paths lead to cleanup
grep -r "add_edge\|add_conditional_edges" agent/nodes/voice/ | \
  grep -v "cleanup" | \
  # Check that all edges either:
  #   1. Go to cleanup directly, OR
  #   2. Go to a node that eventually goes to cleanup
```

---

**Next**: See `voice-state/spec.md` for VoiceState model definition.
