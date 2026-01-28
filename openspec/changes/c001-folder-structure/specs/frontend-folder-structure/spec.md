# Spec: frontend-folder-structure

**File**: `specs/frontend-folder-structure/spec.md`

## 1.1 Purpose

Define the frontend folder structure for Real AgentX v0.1, following Next.js 15 App Router with atomic state pattern from R014.

## 1.2 Scope

**In Scope**:
- Next.js 15 App Router structure
- Component organization (ui/, descriptors/, layout/)
- State management with Zustand + Immer
- Atomic state pattern for widgets
- Type definitions

**Out of Scope**:
- Backend structure (see backend-folder-structure spec)
- WebSocket protocol (see C003-agent-pipeline)

## 1.3 Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-FRONTEND-001 | Frontend SHALL use Next.js 15 App Router | Must |
| FR-FRONTEND-002 | Components SHALL be organized in components/ui/, components/descriptors/, components/layout/ | Must |
| FR-FRONTEND-003 | State SHALL use Zustand with Immer | Must |
| FR-FRONTEND-004 | Widget state SHALL use atomic slice pattern | Must |
| FR-FRONTEND-005 | Types SHALL be defined in types/ directory | Must |
| FR-FRONTEND-006 | Hooks SHALL be in hooks/ directory | Must |
| FR-FRONTEND-007 | No component SHALL exceed 300 lines | Must |
| FR-FRONTEND-008 | All TypeScript SHALL pass `npx tsc --noEmit` | Must |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-FRONTEND-001 | Atomic state pattern prevents cascade re-renders | Must |
| NFR-FRONTEND-002 | Widget components use collocated state | Should |
| NFR-FRONTEND-003 | Types synchronized with backend Pydantic models | Must (see C002) |

## 1.4 Data Model

```typescript
// Atomic state pattern from R014 (concept, not names)
// Prevents cascade re-renders when widgets are added/removed
interface WidgetStore {
  // Separate slices for each widget (not Record<string, Widget>)
  widget_abc123_data: UIDescriptor
  widget_abc123_viewState: ViewState
  widget_abc123_position: Position
  widget_def456_data: UIDescriptor
  widget_def456_viewState: ViewState
  // ... each widget gets its own top-level slice
}
```

**Placement**: `/home/riju279/Documents/Code/XRIG/AgentX/frontend/store/widget-store.ts`

## 1.5 API Contract

*None for this spec - see C002-data-contracts*

## 1.6 Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-FRONTEND-001 | Components < 300 lines | Code review, split sub-components |
| BR-FRONTEND-002 | Atomic state for widgets | Code review (no Record<string, Widget>) |
| BR-FRONTEND-003 | Types synchronized with backend | Build check with tsc |

## 1.7 Acceptance Criteria

- [ ] All directories exist with correct structure
- [ ] Atomic state pattern implemented for widgets
- [ ] All components < 300 lines
- [ ] All TypeScript passes `npx tsc --noEmit`
- [ ] Zustand stores use Immer for updates
