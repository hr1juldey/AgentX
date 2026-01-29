# Delta Spec: c001-folder-structure

**File**: `specs/frontend-folder-structure/spec.md`

**Generated**: 2026-01-29
**Change**: c001-folder-structure
**Related**: c010-voice-client

---

## ADDED Requirements

### Requirement: Voice Client Components in Frontend Structure

The frontend folder structure MUST include voice client components for external kyutai voice-server integration.

#### Scenario: Voice client components exist

- **WHEN** c010-voice-client is implemented
- **THEN** lib/voice/client.ts exists with VoiceClient class
- **AND** lib/voice/types.ts exists with TypeScript types for voice protocol
- **AND** lib/voice/conversation.ts exists with conversation state helpers
- **AND** types/voice-protocol.ts exists with Zod schemas for voice protocol
- **AND** all components follow Next.js 15 App Router patterns

---

## MODIFIED Requirements

### Requirement: Frontend Lib Directory

The frontend/lib/ directory MUST include voice client library alongside other client libraries.

**Migration Path**: Add lib/voice/ subdirectory without modifying existing structure.

#### Scenario: Voice client library added

- **WHEN** c010-voice-client is implemented
- **THEN** frontend/lib/voice/ directory exists
- **AND** frontend/lib/voice/ contains client.ts, types.ts, conversation.ts
- **AND** all TypeScript files pass type checking (tsc --noEmit)
- **AND** all files follow project naming conventions

---

**Related Changes**:
- c010-voice-client - Voice client infrastructure implementation
