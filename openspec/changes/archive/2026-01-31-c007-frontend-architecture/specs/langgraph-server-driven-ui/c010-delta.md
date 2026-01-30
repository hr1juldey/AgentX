# Delta Spec: c007-frontend-architecture

**File**: `specs/langgraph-server-driven-ui/spec.md`

**Generated**: 2026-01-29
**Change**: c007-frontend-architecture
**Related**: c010-voice-client

---

## MODIFIED Requirements

### Requirement: Voice Client Components in Frontend Architecture

The frontend architecture MUST include voice client components for WebSocket connections to AgentX voice services.

**Migration Path**: Add lib/voice/ directory to frontend structure.

#### Scenario: Voice client components integrated

- **WHEN** c010-voice-client is implemented
- **THEN** frontend/lib/voice/client.ts provides VoiceClient for WebSocket connections
- **AND** VoiceClient connects to AgentX WebSocket on port 8019
- **AND** VoiceClient sends Audio messages with base64-encoded audio
- **AND** VoiceClient receives and plays TTS audio chunks
- **AND** VoiceClient handles interrupt messages
- **AND** VoiceClient reconnects with exponential backoff
- **AND** types/voice-protocol.ts provides Zod schemas for voice protocol
- **AND** all voice components integrate with LangGraph server-driven UI

---

**Related Changes**:
- c010-voice-client - Voice client infrastructure implementation
