# Delta Spec: c003-agent-pipeline

**File**: `specs/dspy-main-agent/spec.md`

**Generated**: 2026-01-29
**Change**: c003-agent-pipeline
**Related**: c010-voice-client

---

## MODIFIED Requirements

### Requirement: Voice Integration via VoiceGatewayService

The agent pipeline MUST integrate with voice interaction via VoiceGatewayService instead of direct internal voice service calls.

**Migration Path**: Update ExecuteAgentQueryUseCase to support conversational context from ConversationStateManager.

#### Scenario: Voice query with conversational context

- **WHEN** voice query is received via VoiceGatewayService
- **THEN** ExecuteAgentQueryUseCase receives conversation history from ConversationStateManager
- **AND** ExecuteAgentQueryUseCase receives conversation context (topic, entities, sentiment)
- **AND** Agent processes query with conversation context awareness
- **AND** Agent response is returned with UI widgets via server-driven UI

#### Scenario: Context injection into agent query

- **WHEN** user sends follow-up question (e.g., "And in New York?")
- **THEN** ConversationStateManager provides conversation history
- **AND** ConversationContext contains topic="weather", entities=["San Francisco"]
- **THEN** ExecuteAgentQueryRequest includes conversation context
- **AND** Agent response references previous context
- **AND** ConversationStateManager tracks assistant response

---

**Related Changes**:
- c010-voice-client - Voice gateway and conversational state infrastructure
