# Delta Spec: c001-folder-structure

**File**: `specs/backend-folder-structure/spec.md`

**Generated**: 2026-01-29
**Change**: c001-folder-structure
**Related**: c010-voice-client

---

## ADDED Requirements

### Requirement: Voice Client Components in Backend Structure

The backend folder structure MUST include voice client components for external kyutai voice-server integration.

#### Scenario: Voice client components exist

- **WHEN** c010-voice-client is implemented
- **THEN** domain/entities/conversation_session.py exists with ConversationSession entity
- **AND** application/dtos/voice_gateway_dtos.py exists with KyutaiMessage model
- **AND** application/use_cases/conversation_state_manager.py exists with ConversationStateManager class
- **AND** infrastructure/external/voice_gateway_service.py exists with VoiceGatewayService class
- **AND** infrastructure/external/voice_protocol.py exists with kyutai protocol helpers
- **AND** infrastructure/external/text_stream_handler.py exists with TextStreamHandler class
- **AND** all files follow Clean Architecture layer separation

---

## MODIFIED Requirements

### Requirement: Infrastructure External Services

The infrastructure/external/ directory MUST include voice gateway services for external kyutai integration alongside existing external services.

**Migration Path**: Add voice client services to infrastructure/external/ without removing existing services.

#### Scenario: Voice gateway services added

- **WHEN** c010-voice-client is implemented
- **THEN** infrastructure/external/ includes voice_gateway_service.py
- **AND** infrastructure/external/ includes voice_protocol.py
- **AND** infrastructure/external/ includes text_stream_handler.py
- **AND** all services follow Clean Architecture patterns
- **AND** all services pass CLAUDE_POLICY.md compliance checks

---

**Related Changes**:
- c010-voice-client - Voice client infrastructure implementation
