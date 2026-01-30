# Tasks Artifact: c010-voice-client

**Generated**: 2026-01-29
**Change**: c010-voice-client
**Schema**: spec-driven v1

---

## Summary

Implement voice client infrastructure for external kyutai voice-server integration. This change shifts AgentX from internal voice service implementation (VAD, STT, TTS) to external kyutai service dependency, focusing on fast async text stream handling and conversational state management.

**Total Tasks**: 57 tasks across 8 phases (Phases 1-5: 48/48 complete, Phase 6: 11/11 complete, Phase 7: 9/9 complete, Phase 8: 15/15 SDK integration)

**Status**: All 83 tasks complete! Ready for verification checklist.

---

## 1. Data Contracts & Types

**Goal**: Define Pydantic models and Zod schemas for kyutai protocol and conversational state.

- [x] 1.1 Create `agentx/application/dtos/voice_gateway_dtos.py` with KyutaiMessage, KyutaiMessageType models
- [x] 1.2 Create `agentx/domain/entities/conversation_session.py` with ConversationSession, ConversationMessage, ConversationContext entities
- [x] 1.3 Create `frontend/types/voice-protocol.ts` with Zod schemas matching Pydantic models
- [x] 1.4 Create `frontend/lib/voice/types.ts` with TypeScript types for voice client
- [x] 1.5 Verify Pydantic ↔ Zod sync (field aliases, enum values, optional fields)
- [x] 1.6 Run type checking (tsc --noEmit, pyright) and verify no errors

---

## 2. Backend Infrastructure

**Goal**: Implement backend voice gateway and stream handling services.

- [x] 2.1 Create `agentx/infrastructure/external/voice_protocol.py` with kyutai protocol helpers
- [x] 2.2 Create `agentx/infrastructure/external/text_stream_handler.py` with TextStreamHandler, STTBuffer classes
- [x] 2.3 Create `agentx/infrastructure/external/voice_gateway_service.py` with VoiceGatewayService class
- [x] 2.4 Implement VoiceGatewayService.handle_session() for frontend WebSocket management
- [x] 2.5 Implement VoiceGatewayService._input_task() for routing audio to kyutai STT
- [x] 2.6 Implement VoiceGatewayService._output_task() for receiving from kyutai
- [x] 2.7 Implement VoiceGatewayService._process_agent_response() for C003 integration
- [x] 2.8 Implement VoiceGatewayService.check_kyutai_health() for health check
- [x] 2.9 Implement TextStreamHandler.buffer_stt_chunk() for STT buffering
- [x] 2.10 Implement TextStreamHandler.split_tts_sentences() for TTS sentence splitting
- [x] 2.11 Implement TextStreamHandler.stream_tts_sentences() for TTS streaming with interruption
- [x] 2.12 Run ruff check --fix, ruff format, pyrefly check --summarize-errors
- [x] 2.13 Verify all files under 150 lines (CLAUDE_POLICY.md Rule 3)

---

## 3. Backend Application Layer

**Goal**: Implement conversational state management use case.

- [x] 3.1 Create `agentx/application/use_cases/conversation_state_manager.py` with ConversationStateManager class
- [x] 3.2 Implement ConversationStateManager.get_or_create_session() for session CRUD
- [x] 3.3 Implement ConversationStateManager.add_user_message() for tracking user input
- [x] 3.4 Implement ConversationStateManager.add_assistant_message() for tracking agent response
- [x] 3.5 Implement ConversationStateManager.get_conversation_history() for history retrieval
- [x] 3.6 Implement ConversationStateManager.update_context() for context updates
- [x] 3.7 Implement ConversationStateManager._cleanup_expired_sessions() for session cleanup
- [x] 3.8 Implement ConversationStateManager.start() and stop() for cleanup task management
- [x] 3.9 Run ruff check --fix, ruff format, pyrefly check --summarize-errors
- [x] 3.10 Verify file under 150 lines (CLAUDE_POLICY.md Rule 3)

---

## 4. Frontend Voice Client

**Goal**: Implement frontend voice client for WebSocket connections.

- [x] 4.1 Create `frontend/lib/voice/client.ts` with VoiceClient class
- [x] 4.2 Implement VoiceClient.connect() for WebSocket connection
- [x] 4.3 Implement VoiceClient.send_audio() for sending audio chunks
- [x] 4.4 Implement VoiceClient.send_interrupt() for interruption
- [x] 4.5 Implement VoiceClient.on() for message handler registration
- [x] 4.6 Implement VoiceClient.reconnect() with exponential backoff
- [x] 4.7 Implement VoiceClient.disconnect() for cleanup
- [x] 4.8 Create `frontend/lib/voice/conversation.ts` with conversation state helpers
- [x] 4.9 Run ESLint check, TypeScript type check (tsc --noEmit)
- [x] 4.10 Verify no TypeScript errors

---

## 5. Backend API Routes

**Goal**: Implement REST and WebSocket endpoints for voice interaction.

- [x] 5.1 Update `agentx/presentation/api/v1/voice_routes.py` with new endpoints
- [x] 5.2 Implement GET /api/v1/voice/kyutai/status for health check
- [x] 5.3 Implement GET /api/v1/voice/conversation/history for session history
- [x] 5.4 Implement POST /api/v1/voice/conversation/context for context updates
- [x] 5.5 Update WebSocket /ws/voice endpoint to use VoiceGatewayService
- [x] 5.6 Update WebSocket handler to integrate ConversationStateManager
- [x] 5.7 Update WebSocket handler to integrate TextStreamHandler
- [x] 5.8 Run ruff check --fix, ruff format, pyrefly check --summarize-errors
- [x] 5.9 Verify files under 150 lines (CLAUDE_POLICY.md Rule 3)

---

## 6. Integration & Testing

**Goal**: Integrate all components and verify end-to-end functionality.

- [x] 6.1 Wire VoiceGatewayService into voice_routes.py dependency injection
- [x] 6.2 Wire ConversationStateManager into voice pipeline
- [x] 6.3 Wire TextStreamHandler into voice pipeline
- [x] 6.4 Test frontend → AgentX → kyutai STT flow
- [x] 6.5 Test kyutai STT → AgentX → C003 → kyutai TTS flow
- [x] 6.6 Test conversation history tracking across multiple turns
- [x] 6.7 Test context injection into C003 agent queries
- [x] 6.8 Test interruption handling during TTS playback
- [x] 6.9 Test graceful degradation when kyutai unavailable
- [x] 6.10 Test WebSocket reconnection with exponential backoff
- [x] 6.11 Verify end-to-end latency <500ms (P95), target <300ms (P50)

---

## 7. Migration & Cleanup

**Goal**: Migrate from internal voice services to external kyutai integration.

- [x] 7.1 Add feature flag USE_KYUTAI_EXTERNAL=true to voice_routes.py
- [x] 7.2 Update documentation to recommend external kyutai integration
- [x] 7.3 Add deprecation notices to VADService, STTService, TTSService
- [x] 7.4 Update c004 tasks.md to reference c010 for voice implementation
- [x] 7.5 Verify coexistence with internal services (Phase 1)
- [x] 7.6 Set feature flag default to USE_KYUTAI_EXTERNAL=true (Phase 2)
- [x] 7.7 Plan Phase 3 removal of deprecated internal services
- [x] 7.8 Update CLAUDE.md with voice client architecture
- [x] 7.9 Verify all documentation updated

---

## 8. Voice Client SDK Integration (Hybrid Adapter Pattern)

**Goal**: Integrate voice_client SDK as internal dependency with fallback to direct WebSocket.

**Background**: After exploring the kyutai voice_client SDK at `/home/riju279/Documents/Tools/kyutai/delayed-streams-modeling/voice_client/`, we identified production-ready patterns for reconnection, encoding, and audio handling. This phase implements a hybrid adapter pattern that uses the SDK internally while maintaining AgentX's public API.

- [x] 8.1 Add voice_client SDK to pyproject.toml as optional dependency
- [x] 8.2 Add USE_VOICE_SDK feature flag to config.py (default: false)
- [x] 8.3 Create agentx/infrastructure/external/voice_sdk_adapter.py with VoiceSDKAdapter class
- [x] 8.4 Implement VoiceSDKAdapter._init_sdk_client() for VoiceClient initialization
- [x] 8.5 Implement VoiceSDKAdapter._map_sdk_session_to_agentx() for session mapping
- [x] 8.6 Implement VoiceSDKAdapter.handle_via_sdk() using VoiceClient.converse()
- [x] 8.7 Implement VoiceSDKAdapter.handle_via_direct_ws() fallback path
- [x] 8.8 Update VoiceGatewayService to use VoiceSDKAdapter based on feature flag
- [x] 8.9 Add logging at adapter boundaries for debugging (SDK messages, mapped sessions)
- [x] 8.10 Test SDK path: frontend → Adapter → SDK → kyutai → frontend
- [x] 8.11 Test fallback path: frontend → Adapter → direct WebSocket → kyutai
- [x] 8.12 Test session mapping: SDK UUID → AgentX conversation_id
- [x] 8.13 Test feature flag switching between SDK and direct modes
- [x] 8.14 Run ruff check --fix, ruff format, pyrefly check --summarize-errors
- [x] 8.15 Verify adapter file under 150 lines (split if needed)

---

## Verification Checklist

**Data Contracts**:
- [ ] KyutaiMessage Pydantic model validates kyutai protocol
- [ ] KyutaiMessage Zod schema matches Pydantic model exactly
- [ ] ConversationSession entity tracks session state correctly
- [ ] Field aliases map snake_case → camelCase
- [ ] Enum values match exactly (case-sensitive)

**Backend Services**:
- [ ] VoiceGatewayService connects to kyutai STT/TTS WebSockets
- [ ] VoiceGatewayService routes messages correctly (frontend ↔ kyutai)
- [ ] ConversationStateManager tracks messages and context
- [ ] TextStreamHandler buffers STT transcripts until Eos
- [ ] TextStreamHandler splits TTS input into sentences
- [ ] All files pass ruff check, ruff format, pyrefly check
- [ ] All files under 150 lines

**Frontend Client**:
- [ ] VoiceClient connects to AgentX WebSocket
- [ ] VoiceClient sends Audio messages to AgentX
- [ ] VoiceClient receives and plays TTS audio
- [ ] VoiceClient handles interrupt messages
- [ ] VoiceClient reconnects with exponential backoff
- [ ] All TypeScript files pass type check

**Integration**:
- [ ] End-to-end voice interaction works (speech → speech)
- [ ] Conversation history tracked across turns
- [ ] Context injected into C003 agent queries
- [ ] Interruption terminates TTS within 200ms
- [ ] Graceful degradation when kyutai unavailable
- [ ] Latency targets met (<500ms P95, <300ms P50)

**Migration**:
- [ ] Feature flag switches between internal/external services
- [ ] Deprecation notices added to internal services
- [ ] Documentation updated with new architecture
- [ ] CLAUDE.md reflects voice client changes

---

**Total Estimated Tasks**: 42 tasks

**Completion Criteria**:
- All tasks checked off
- All verification criteria met
- End-to-end voice interaction functional
- Latency targets achieved
- All quality checks pass (ruff, pyrefly, ESLint, TypeScript)

---

**Related Changes**:
- C003-agent-pipeline - Agent pipeline integration
- C002-data-contracts - Data contract updates
- C001-folder-structure - Folder structure updates
- C007-frontend-architecture - Frontend architecture

---
