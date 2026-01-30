# Tasks Artifact: c004-voice-streaming

**Generated**: 2026-01-28
**Change**: c004-voice-streaming
**Schema**: spec-factory v1

**IMPORTANT (2026-01-31):** This change is **DEPRECATED** in favor of **C010-voice-client**, which implements external kyutai voice-server integration. The internal voice services (VADService, STTService, TTSService) described here are superseded by `VoiceGatewayService`. See [`openspec/changes/c010-voice-client/`](../c010-voice-client/) for the current implementation.

---

## 1. Implementation Status

**⚠️ DEPRECATED (2026-01-31):** This change is **superseded by C010-voice-client**.

### 1.1 Reason for Deprecation

C004 was designed to implement internal voice services (VAD, STT, TTS) running locally. However, **C010-voice-client** was completed first and implements a superior architecture using external kyutai voice-server integration.

| Aspect | C004 (Internal) | C010 (External) | Winner |
|--------|-----------------|-----------------|--------|
| **Architecture** | Internal VAD/STT/TTS services | External kyutai integration | C010 |
| **Model management** | Local model loading (~7GB) | No local models | C010 |
| **Latency** | VAD<50ms + STT<200ms + TTS<100ms | Network to kyutai (<100ms) | C010 |
| **Maintenance** | Model updates, memory management | External service updates | C010 |
| **Complexity** | 3 services + pipeline | 1 VoiceGatewayService | C010 |

### 1.2 C010 Implementation Details

**Completed 2026-01-31**: C010-voice-client (111/111 tasks)

| Component | File | Purpose |
|-----------|------|---------|
| `VoiceGatewayService` | `infrastructure/external/voice_gateway_service.py` | Main service for kyutai integration |
| `ConversationStateManager` | `application/use_cases/conversation_state_manager.py` | Session/conversation tracking |
| `TextStreamHandler` | `infrastructure/external/text_stream_handler.py` | STT buffering + TTS streaming |
| `VoiceSDKAdapter` | `infrastructure/external/voice_sdk_adapter.py` | Hybrid SDK/Direct WebSocket adapter |
| Voice routes | `presentation/api/v1/voice_routes.py` | REST + WebSocket endpoints |

### 1.3 Implementation Tasks (All Skipped)

All implementation tasks are **skipped** due to deprecation:

| Phase | Tasks | Status |
|-------|-------|--------|
| Phase 1: Voice Services | 4 tasks | ⏭️ Skipped (C010 supersedes) |
| Phase 2: Domain/Application | 4 tasks | ⏭️ Skipped (C010 supersedes) |
| Phase 3: Presentation | 3 tasks | ⏭️ Skipped (C010 supersedes) |
| Phase 4: Frontend | 3 tasks | ⏭️ Skipped (C010 supersedes) |
| Phase 5: Testing | 5 tasks | ⏭️ Skipped (C010 supersedes) |

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

C004-voice-streaming is **superseded** by C010-voice-client.

**Status**: ⚠️ DEPRECATED (2026-01-31)

**Reason**: C010 implements external kyutai voice-server integration, which is superior to the internal voice services architecture planned for C004.

**Replacement**: All voice functionality is now implemented in:
- **C010-voice-client** (111/111 tasks complete)
  - `VoiceGatewayService` - External kyutai integration
  - `ConversationStateManager` - Session/conversation tracking
  - `TextStreamHandler` - STT buffering + TTS streaming
  - `VoiceSDKAdapter` - Hybrid SDK/Direct WebSocket adapter

**Artifacts Complete**:
- [x] All 7 artifacts created (scan, extract, validate, proposal, specs, design, tasks)
- [x] Deprecation notice added
- [x] Superseding change (C010) documented

**Implementation Skipped**:
- ⏭️ All implementation phases skipped (C010 provides superior implementation)

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

C004-voice-streaming is **superseded by C010**. No implementation verification required.

**Artifacts Status**:
- [x] All 7 artifacts created (scan, extract, validate, proposal, specs, design, tasks)
- [x] Deprecation notice documented
- [x] C010 replacement documented

**Implementation Status**: ⏭️ **SKIPPED** - C010 provides superior implementation

**C010 Voice Functionality** (replaces C004):
- [x] VoiceGatewayService implements external kyutai integration
- [x] ConversationStateManager tracks sessions/messages/context
- [x] TextStreamHandler handles STT buffering + TTS streaming
- [x] VoiceSDKAdapter provides hybrid SDK/Direct WebSocket adapter
- [x] Voice routes updated (REST + WebSocket)
- [x] Frontend voice client implemented (client.ts, conversation.ts)
- [x] All quality checks pass (ruff, pyrefly, ESLint, TypeScript)
- [x] End-to-end voice interaction functional

---

**End of spec-factory pipeline**
