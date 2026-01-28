# Proposal: c004-voice-streaming

**Generated**: 2026-01-28
**Change**: c004-voice-streaming
**Schema**: spec-factory v1

---

## Summary

Implement streaming voice interface for AgentX with VAD filtering, STT transcription, LLM integration via C003 agent pipeline, and TTS synthesis. System supports full-duplex WebSocket communication with <500ms end-to-end latency target and interruption handling.

---

## Motivation

### Problem Statement

Current AgentX prototypes require text input, limiting accessibility and natural interaction. Voice interface enables hands-free operation, mobile use cases, and more natural human-AI interaction. However, voice interfaces face challenges:

1. **Latency**: Turn-based voice assistants feel sluggish (>1s response time)
2. **Interruption**: Cannot interrupt AI speech, feels unnatural
3. **Silence Processing**: Wastes resources buffering and processing silence
4. **Memory Leaks**: TTS models grow unbounded (observed 32GB+ in R011)

### Current State

- **R011 Personal Assistant**: Basic STT/TTS integration with Silero
  - Single WebSocket task (no bidirectional streaming)
  - No VAD filtering (processes silence)
  - No interruption handling
  - Memory leaks in TTS (no reload strategy)
  - Combined STT+VAD service (tight coupling)

- **C003 Agent Pipeline**: DSPy agents ready for integration
  - ExecuteAgentQueryUseCase available for STT → LLM
  - StreamUIUpdateUseCase available for LLM → TTS

### Desired State

Production voice interface with:
- **Streaming Pipeline**: Full duplex WebSocket with <500ms latency
- **VAD Filtering**: Silero VAD filters silence before STT
- **Interruption**: VAD monitoring during TTS for early termination
- **Memory Management**: Periodic TTS model reload to prevent leaks
- **Clean Separation**: VAD, STT, TTS services decoupled

---

## Scope

### In Scope

- **VAD Service**: Silero VAD integration with <50ms processing
- **STT Service**: Kyutai STT 2.6B integration with audio resampling
- **TTS Service**: Pocket TTS integration with streaming output and memory management
- **Voice Pipeline**: Orchestration of VAD → STT → LLM → TTS flow
- **WebSocket Endpoints**: Bidirectional audio streaming on port 8019
- **REST Endpoints**: Session management on port 8018
- **Integration**: C003 agent pipeline for LLM processing
- **Interruption Handling**: VAD monitoring during TTS generation

### Out of Scope

- **Voice Wake Word**: "Hey AgentX" activation (future feature)
- **Speaker Recognition**: User identification via voice (future feature)
- **Multi-Language**: English only initially (Kyutai STT 2.6B-en)
- **Emotion Control**: TTS emotion parameterization (future feature)
- **Voice Cloning**: Custom voice generation (future feature)

### Dependencies

| Change | Status | Required For |
|--------|--------|--------------|
| **C001-folder-structure** | Complete | Clean Architecture layers for voice services |
| **C002-data-contracts** | Complete | WebSocket message types (AUDIO_CHUNK, TRANSCRIPT, etc.) |
| **C003-agent-pipeline** | Complete | ExecuteAgentQueryUseCase for LLM integration |

---

## Success Criteria

1. **End-to-End Latency**: <500ms from speech start to audio response
   - Measure: Time from first audio chunk received to first TTS chunk sent
   - Target: P95 < 500ms, P50 < 300ms

2. **VAD Accuracy**: >95% speech probability accuracy
   - Measure: Manual testing with silence/speech mix
   - Target: <5% false positives (silence detected as speech)

3. **STT Accuracy**: >90% word accuracy on clear speech
   - Measure: Word error rate on test set
   - Target: WER < 10%

4. **Interruption Latency**: <200ms to terminate TTS on interrupt
   - Measure: Time from interrupt signal to TTS stop
   - Target: P95 < 200ms

5. **Memory Stability**: <2GB after 1 hour of operation
   - Measure: Peak memory usage over 1-hour stress test
   - Target: No unbounded growth, periodic reloads effective

6. **Concurrent Sessions**: Support 5 simultaneous voice sessions
   - Measure: 5 concurrent WebSocket connections
   - Target: No degradation, latency maintained

7. **Policy Compliance**: 100% CLAUDE_POLICY.md compliance
   - Measure: `ruff check`, `ruff format`, import validation
   - Target: Zero violations

---

## Implementation Approach

### High-Level Approach

1. **Create Voice Services** (infrastructure layer)
   - VADService: Silero VAD with resampling
   - STTService: Kyutai STT 2.6B with audio preprocessing
   - TTSService: Pocket TTS with streaming and reload

2. **Create Voice Pipeline** (application layer)
   - VoicePipelineUseCase: Orchestrates VAD → STT → LLM → TTS
   - Integration with ExecuteAgentQueryUseCase from C003

3. **Create WebSocket Endpoints** (presentation layer)
   - `/ws/voice`: Full duplex audio streaming (port 8019)
   - Separate input_task and output_task for bidirectional flow
   - Interruption handling via INTERRUPT message type

4. **Create REST Endpoints** (presentation layer)
   - `/api/v1/voice/session`: Session management (port 8018)
   - `/api/v1/voice/health`: Health check (port 8020)

### Key Decisions

| Decision | Rationale | Alternatives Considered |
|----------|-----------|------------------------|
| **Pocket TTS (100M params)** | Low latency (<200ms), CPU-only, good quality | Silero TTS (variable API), ElevenLabs (paid, high latency) |
| **Kyutai STT 2.6B** | Streaming support, good accuracy, free | Whisper (higher latency), AssemblyAI (paid) |
| **Silero VAD** | <50ms latency, probability-based, CPU-only | WebRTC VAD (less accurate), custom model (complex) |
| **500ms audio chunks** | Low latency, manageable memory | 250ms (too many messages), 1s (too high latency) |
| **Separate VAD/STT/TTS services** | Testability, reusability, single responsibility | Combined service (R011 pattern, tight coupling) |
| **Full duplex WebSocket** | Interruption requires simultaneous I/O | Half-duplex (can't interrupt, feels unnatural) |
| **Ports 8018-8020** | Avoids 8000-8017 (C003) and 8080 (SearXNG) | 8000-8014 (reserved), 8080 (SearXNG conflict) |

### Constraints

- **Ports**: Use 8018-8020 (avoid 8000-8014, 8080)
- **File size**: Max 100 lines executable + 50 overhead (CLAUDE_POLICY.md)
- **Imports**: Absolute only, no `from .` or `from ..` (CLAUDE_POLICY.md)
- **Ruff**: Must pass `ruff check --fix` and `ruff format`
- **Audio formats**: STT requires 16kHz, TTS outputs 24kHz or 48kHz
- **Latency**: <500ms end-to-end target

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **TTS memory leak** | High | High | Periodic model reload every N generations, memory monitoring |
| **High latency** | Medium | High | Streaming pipeline (not turn-based), VAD filtering, small chunks |
| **STT accuracy** | Medium | Medium | Use Kyutai STT 2.6B (high quality), resample to 16kHz |
| **WebSocket disconnection** | Medium | Medium | Auto-reconnect logic, session state persistence |
| **Model loading time** | Low | Medium | Load models on startup, health check waits for ready |
| **Port conflicts** | Low | Low | Use 8018-8020 (checked against reserved ports) |
| **Interruption race conditions** | Medium | Medium | Atomic interrupt flag, checked in TTS generation loop |
| **Concurrent session scaling** | Low | Low | Limit to 5 sessions initially, monitor resources |

---

## Open Questions

1. **TTS Model Reload Interval**
   - Question: How often to reload Pocket TTS model to prevent memory leaks?
   - Recommendation: Every 100 TTS generations (~5-10 minutes of continuous speech)
   - Resolution: Set as configurable parameter, default to 100

2. **Audio Chunk Size for Different Networks**
   - Question: Should 500ms chunks be adjusted for mobile vs desktop?
   - Recommendation: Start with 500ms, monitor and adjust based on telemetry
   - Resolution: Make chunk size configurable, default to 500ms

3. **VAD Threshold Tuning**
   - Question: What speech probability threshold for VAD filtering?
   - Recommendation: Start with 0.5 (default Silero), adjust based on testing
   - Resolution: Make threshold configurable, default to 0.5

4. **Interrupt Detection Window**
   - Question: How long to detect speech before confirming interruption?
   - Recommendation: 200ms of continuous speech during TTS
   - Resolution: Make window configurable, default to 200ms

5. **LLM Streaming Integration**
   - Question: Should we stream LLM tokens to TTS or wait for complete response?
   - Recommendation: Wait for complete response (simpler, better coherence)
   - Resolution: Start with complete response, add streaming as optimization

---

**Next Artifact**: specs.md
