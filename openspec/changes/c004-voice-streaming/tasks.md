# Tasks Artifact: c004-voice-streaming

**Generated**: 2026-01-28
**Change**: c004-voice-streaming
**Schema**: spec-factory v1

**IMPORTANT (2026-01-31):** This change is **DEPRECATED** in favor of **C010-voice-client**, which implements external kyutai voice-server integration. The internal voice services (VADService, STTService, TTSService) described here are superseded by `VoiceGatewayService`. See [`openspec/changes/c010-voice-client/`](../c010-voice-client/) for the current implementation.

---

## 1. Implementation Checklist

### 1.1 Phase 1: Voice Services (Infrastructure Layer)

| Task | File | Lines (est.) | Status | Notes |
|------|------|--------------|--------|-------|
| Create VADService | `infrastructure/external/vad_service.py` | 80 | ⬜ | Silero VAD, resampling, <50ms latency |
| Create STTService | `infrastructure/external/stt_service.py` | 100 | ⬜ | Kyutai STT 2.6B, preprocessing |
| Create TTSService | `infrastructure/external/tts_service.py` | 120 | ⬜ | Pocket TTS, streaming, reload strategy |
| Create voice config | `core/voice_config.py` | 50 | ⬜ | Voice service settings |

### 1.2 Phase 2: Domain and Application Layer

| Task | File | Lines (est.) | Status | Notes |
|------|------|--------------|--------|-------|
| Create VoiceSessionEntity | `domain/entities/voice_session.py` | 80 | ⬜ | @dataclass, state transitions |
| Create VoiceSessionRepository | `domain/repositories/voice_session_repository.py` | 60 | ⬜ | In-memory session storage |
| Create VoicePipelineUseCase | `application/use_cases/voice_pipeline_use_case.py` | 120 | ⬜ | Orchestrate VAD → STT → LLM → TTS |
| Create voice DTOs | `application/dtos/voice_dtos.py` | 80 | ⬜ | AudioChunkMessage, TranscriptMessage, etc. |

### 1.3 Phase 3: Presentation Layer

| Task | File | Lines (est.) | Status | Notes |
|------|------|--------------|--------|-------|
| Create voice routes | `presentation/api/v1/voice_routes.py` | 100 | ⬜ | REST endpoints + WebSocket handler |
| Create WebSocket handler | `presentation/api/v1/voice_websocket.py` | 80 | ⬜ | Full duplex input/output tasks |
| Create health check | `presentation/api/v1/voice_health.py` | 40 | ⬜ | Service readiness endpoint |

### 1.4 Phase 4: Frontend Types

| Task | File | Lines (est.) | Status | Notes |
|------|------|--------------|--------|-------|
| Create voice types | `frontend/types/voice.ts` | 100 | ⬜ | Zod schemas matching Pydantic |
| Create voice hooks | `frontend/hooks/useVoiceWebSocket.ts` | 80 | ⬜ | WebSocket connection, audio handling |
| Create voice components | `frontend/components/VoiceInterface.tsx` | 120 | ⬜ | Recording, playback, interrupt button |

### 1.5 Phase 5: Testing

| Task | Type | Status | Notes |
|------|------|--------|-------|
| Unit tests for VADService | `tests/unit/test_vad_service.py` | ⬜ | Mock audio, verify probability |
| Unit tests for STTService | `tests/unit/test_stt_service.py` | ⬜ | Mock model, verify resampling |
| Unit tests for TTSService | `tests/unit/test_tts_service.py` | ⬜ | Mock model, verify streaming |
| Integration tests | `tests/integration/test_voice_pipeline.py` | ⬜ | End-to-end voice flow |
| WebSocket tests | `tests/integration/test_voice_websocket.py` | ⬜ | Full duplex communication |

---

## 2. Verification Steps

### 2.1 Code Quality

```bash
# Run all quality checks
cd /home/riju279/Documents/Code/XRIG/AgentX/agentx
ruff check . --fix
ruff format .
pyrefly check . --summarize-errors

# Frontend type check
cd /home/riju279/Documents/Code/XRIG/AgentX/frontend
npx tsc --noEmit
```

### 2.2 File Size Validation

```bash
# Verify no file exceeds 150 lines
find agentx/ -name "*.py" -exec wc -l {} + | awk '$1 > 150 {print "FILE TOO LARGE:", $2}'

# Voice services specifically
wc -l agentx/infrastructure/external/vad_service.py
wc -l agentx/infrastructure/external/stt_service.py
wc -l agentx/infrastructure/external/tts_service.py
```

### 2.3 Import Validation

```bash
# Verify no relative imports (forbidden by CLAUDE_POLICY.md)
grep -r "from \.\." agentx/  # Should return nothing
grep -r "from \." agentx/ | grep -v "from \.\.\."  # Should return nothing

# Verify absolute imports only
grep -r "^from agentx" agentx/ | head -20  # Should show results
```

### 2.4 Model Loading Validation

```bash
# Verify models load correctly
python -c "from infrastructure.external.vad_service import VADService; v = VADService(); print('VAD OK')"
python -c "from infrastructure.external.stt_service import STTService; s = STTService(); print('STT OK')"
python -c "from infrastructure.external.tts_service import TTSService; t = TTSService(); print('TTS OK')"
```

### 2.5 WebSocket Validation

```bash
# Test WebSocket connection
wscat -c "ws://localhost:8019/ws/voice"

# Test REST endpoints
curl http://localhost:8018/api/v1/voice/health
curl -X POST http://localhost:8018/api/v1/voice/session -H "Content-Type: application/json" -d '{}'
```

### 2.6 Integration Tests

```bash
# Run integration tests
pytest tests/integration/test_voice_pipeline.py -v
pytest tests/integration/test_voice_websocket.py -v

# Run stress test (5 concurrent sessions)
pytest tests/integration/test_voice_concurrent.py -v
```

---

## 3. Acceptance Criteria

### 3.1 Functional Criteria

| Criterion | Test Method | Expected Result |
|-----------|-------------|-----------------|
| **VAD filters silence** | Unit test with silence audio | speech_probability < 0.3 |
| **VAD detects speech** | Unit test with speech audio | speech_probability > 0.7 |
| **STT transcribes audio** | Integration test with clear speech | text non-empty, confidence > 0.8 |
| **STT resamples audio** | Unit test with 44.1kHz input | Processes without error |
| **TTS generates audio** | Integration test with text | Returns 24kHz WAV audio |
| **TTS streams chunks** | Integration test, check chunk size | Each chunk ~500ms (12000 samples @ 24kHz) |
| **Pipeline end-to-end** | Integration test, audio in → audio out | <500ms latency, correct response |
| **Interruption works** | Send INTERRUPT during TTS | TTS stops within 200ms |
| **WebSocket full duplex** | Concurrent send/receive | Both directions work |
| **Session lifecycle** | Create → Process → Close | All states transition correctly |

### 3.2 Non-Functional Criteria

| Criterion | Test Method | Expected Result |
|-----------|-------------|-----------------|
| **End-to-end latency** | Benchmark (100 queries) | P95 < 500ms, P50 < 300ms |
| **VAD latency** | Unit test timing | <50ms per chunk |
| **STT latency** | Unit test timing | <200ms per 500ms chunk |
| **TTS first chunk** | Integration test timing | <100ms |
| **Interruption latency** | Time from INTERRUPT to stop | <200ms |
| **Memory stability** | 1-hour stress test | <2GB after reload |
| **Concurrent sessions** | 5 simultaneous WebSocket | No degradation |
| **Code quality** | `ruff check`, `ruff format` | Zero errors |
| **Type checking** | `pyrefly check` | Zero errors |
| **File sizes** | `find + wc` | All files < 150 lines |
| **Import rules** | `grep "from \."` | Zero relative imports |
| **TypeScript compiles** | `npx tsc --noEmit` | Zero errors |

### 3.3 Integration Criteria

| Criterion | Test Method | Expected Result |
|-----------|-------------|-----------------|
| **C001 alignment** | File structure check | Clean Architecture layers match |
| **C002 alignment** | WebSocket message usage | All message types defined |
| **C003 integration** | ExecuteAgentQueryUseCase call | Returns LLM response |
| **Port availability** | netstat/ss check | 8018-8020 not in use |

---

## 4. Definition of Done

C004-voice-streaming is **complete** when:

- [ ] All 3 voice services created (VAD, STT, TTS)
- [ ] VoicePipelineUseCase orchestrates VAD → STT → LLM → TTS flow
- [ ] WebSocket full duplex handler with input/output tasks
- [ ] REST endpoints for session management (port 8018)
- [ ] WebSocket endpoint for streaming (port 8019)
- [ ] Health check endpoint (port 8020)
- [ ] All DTOs created with Pydantic → Zod alignment
- [ ] Frontend Zod schemas match backend Pydantic
- [ ] Zero field name mismatches with LLD
- [ ] Zero relative imports (absolute only)
- [ ] All files under 150 lines
- [ ] All quality checks pass (ruff, pyrefly, tsc)
- [ ] Integration tests pass (VAD, STT, TTS, pipeline)
- [ ] WebSocket full duplex validated
- [ ] Interruption works end-to-end
- [ ] End-to-end latency <500ms (P95)
- [ ] Memory usage stable after 1 hour

---

## 5. Rollback Plan

If implementation fails:

1. **Identify failure point**:
   ```bash
   # Check which test failed
   pytest tests/integration/test_voice_pipeline.py -v

   # Check service health
   curl http://localhost:8018/api/v1/voice/health
   ```

2. **Rollback steps**:
   ```bash
   # Remove created files
   rm -rf agentx/infrastructure/external/vad_service.py
   rm -rf agentx/infrastructure/external/stt_service.py
   rm -rf agentx/infrastructure/external/tts_service.py
   rm -rf agentx/domain/entities/voice_session.py
   rm -rf agentx/domain/repositories/voice_session_repository.py
   rm -rf agentx/application/use_cases/voice_pipeline_use_case.py
   rm -rf agentx/application/dtos/voice_dtos.py
   rm -rf agentx/presentation/api/v1/voice_routes.py
   rm -rf agentx/presentation/api/v1/voice_websocket.py
   rm -rf agentx/presentation/api/v1/voice_health.py
   rm -rf frontend/types/voice.ts
   rm -rf frontend/hooks/useVoiceWebSocket.ts
   rm -rf frontend/components/VoiceInterface.tsx
   ```

3. **Recovery actions**:
   - Re-run from Phase 1 (Voice Services)
   - Verify each model loads independently
   - Test VAD → STT → TTS pipeline step-by-step
   - Add integration tests incrementally

---

## 6. Dependencies Unlocked

This change unlocks:

| Change | Unlocked Feature |
|--------|-----------------|
| **Future: Voice UI Components** | Can add voice-activated UI controls |
| **Future: Multi-modal** | Can combine voice with vision (camera input) |
| **Future: Voice Analytics** | Can track voice interaction patterns |

---

## 7. Verification Checklist

Before marking C004-voice-streaming complete, verify:

- [x] All 7 artifacts created (scan, extract, validate, proposal, specs, design, tasks)
- [ ] All implementation tasks in Phase 1 complete
- [ ] All implementation tasks in Phase 2 complete
- [ ] All implementation tasks in Phase 3 complete
- [ ] All implementation tasks in Phase 4 complete
- [ ] All implementation tasks in Phase 5 complete
- [ ] Code quality checks pass
- [ ] Integration tests pass
- [ ] WebSocket streaming validated
- [ ] Interruption handling validated
- [ ] Latency targets met

---

**End of spec-factory pipeline**
