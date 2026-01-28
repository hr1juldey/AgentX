# Spec: frontend-folder-structure

**File**: `specs/frontend-folder-structure/spec.md`

## 1.1 Purpose

Define the frontend folder structure for Real AgentX v0.1, following Next.js 15 App Router with LangGraph server-driven UI architecture from C007.

## 1.2 Scope

**In Scope**:
- Next.js 15 App Router structure
- LangGraph SDK integration (`useStream`, `LoadExternalComponent`)
- Component organization (ui/, layout/, design/)
- Type definitions
- Organic UI design layer (design/ directory)

**Out of Scope**:
- Backend structure (see backend-folder-structure spec)
- LangGraph server protocol (see C003-agent-pipeline)
- Organic UI visual implementation (see C008-organic-ui)

## 1.3 Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-FRONTEND-001 | Frontend SHALL use Next.js 15 App Router | Must |
| FR-FRONTEND-002 | Components SHALL be organized in components/ui/, components/layout/ | Must |
| FR-FRONTEND-003 | Frontend SHALL use LangGraph SDK (`@langchain/langgraph-sdk/react`) | Must |
| FR-FRONTEND-004 | Frontend SHALL use `LoadExternalComponent` for server-driven UI | Must |
| FR-FRONTEND-005 | Frontend SHALL use `ui_message_reducer` for UI state management | Must |
| FR-FRONTEND-006 | Design tokens SHALL be in design/ directory | Should |
| FR-FRONTEND-007 | Types SHALL be defined in types/ directory | Must |
| FR-FRONTEND-008 | Hooks SHALL be in hooks/ directory | Must |
| FR-FRONTEND-009 | No component SHALL exceed 300 lines | Must |
| FR-FRONTEND-010 | All TypeScript SHALL pass `npx tsc --noEmit` | Must |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-FRONTEND-001 | Server-driven UI prevents state desync | Must |
| NFR-FRONTEND-002 | Shadow DOM provides style isolation | Must |
| NFR-FRONTEND-003 | Designer agent has state awareness | Must (see C003) |
| NFR-FRONTEND-004 | Types synchronized with backend Pydantic models | Must (see C002) |

## 1.4 Data Model

**LangGraph UI State** (from C007 exploration):
```typescript
// Server-driven UI state (no Zustand needed for UI)
interface ThreadState {
  ui: AnyUIMessage[];  // Managed by ui_message_reducer
  messages: BaseMessage[];
}

// UI message structure
interface AnyUIMessage {
  id: string;
  name: string;  // Component name
  props: Record<string, unknown>;
  metadata: Record<string, unknown>;
}
```

**Design Tokens** (from C008 exploration):
```typescript
// design/tokens.ts
export const tokens = {
  color: {
    void: '#0A0A0A',
    membrane: '#141414',
    enzyme: '#00D9FF',
  },
  metaball: {
    desktopBlur: 16,
    mobileBlur: 12,
    mobileMaxBlobs: 6,
    radius: {
      voice: 160,
      voiceMobile: 72,
    }
  }
};
```

**Placement**: `/home/riju279/Documents/Code/XRIG/AgentX/frontend/design/tokens.ts`

## 1.5 API Contract

*See C002-data-contracts for Pydantic ↔ Zod mappings*

**LangGraph SDK Integration**:
```tsx
import { useStream } from "@langchain/langgraph-sdk/react";
import { LoadExternalComponent } from "@langchain/langgraph-sdk/react-ui";
```

## 1.6 Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-FRONTEND-001 | Components < 300 lines | Code review, split sub-components |
| BR-FRONTEND-002 | Use LoadExternalComponent for server UI | Code review |
| BR-FRONTEND-003 | Types synchronized with backend | Build check with tsc |
| BR-FRONTEND-004 | Design tokens used for consistency | Code review |

## 1.7 Acceptance Criteria

- [ ] All directories exist with correct structure
- [ ] LangGraph SDK integration complete
- [ ] LoadExternalComponent renders server components
- [ ] All components < 300 lines
- [ ] All TypeScript passes `npx tsc --noEmit`
- [ ] Design tokens defined and used
- [ ] Shadow DOM prevents style conflicts

## 1.8 ADDED Requirements (from C007 exploration)

### Requirement: LangGraph Server-Driven UI

Frontend SHALL use LangGraph server-driven UI architecture instead of descriptor-only WebSocket pattern.

#### Scenario: Component rendering
- **WHEN** backend emits UI via `push_ui_message()`
- **THEN** frontend receives event via `onCustomEvent` callback
- **AND** `ui_message_reducer` merges update into state
- **AND** `LoadExternalComponent` fetches and renders component
- **AND** component uses Shadow DOM for style isolation

#### Scenario: State awareness
- **WHEN** Designer agent selects widget
- **THEN** agent can access `state.ui` to see existing widgets
- **AND** agent can avoid repeating widgets
- **AND** state is synchronized across all nodes

### Requirement: Organic UI Design Layer

Frontend SHALL include design/ directory for Organic UI visual layer.

#### Scenario: Design tokens
- **WHEN** component needs color or spacing
- **THEN** component imports from design/tokens.ts
- **AND** tokens use void (#0A0A0A), membrane (#141414), enzyme (#00D9FF)
- **AND** metaball settings are platform-aware (16px desktop, 12px mobile)
