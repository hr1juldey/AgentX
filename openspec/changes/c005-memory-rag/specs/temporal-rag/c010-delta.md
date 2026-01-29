# Delta Spec: c005-memory-rag

**File**: `specs/temporal-rag/spec.md`

**Generated**: 2026-01-29
**Change**: c005-memory-rag
**Related**: c010-voice-client

---

## MODIFIED Requirements

### Requirement: Conversational Context for RAG

The memory RAG system MUST integrate with conversational state from voice interactions for better context retrieval.

**Migration Path**: Connect ConversationStateManager with memory consolidation use cases.

#### Scenario: Voice conversation context in RAG

- **WHEN** user asks follow-up question via voice
- **THEN** ConversationStateManager provides conversation history
- **AND** ConversationContext contains topic and entities from previous turns
- **AND** Memory RAG system uses conversation context for better retrieval
- **AND** Agent response incorporates both RAG results and conversation context

---

**Related Changes**:
- c010-voice-client - Conversational state management infrastructure
