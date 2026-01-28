# Spec: langgraph-server-driven-ui

**File**: `specs/langgraph-server-driven-ui/spec.md`

## 1.1 Purpose

Define the LangGraph server-driven UI architecture where the backend has full control over UI rendering by emitting React components via `push_ui_message()`.

## 1.2 Scope

**In Scope**:
- LangGraph SDK installation (`@langchain/langgraph-sdk-react-ui`)
- useStream() hook configuration
- LoadExternalComponent rendering
- Backend widget emission via `push_ui_message()`
- Frontend widget registry (ui.tsx)

**Out of Scope**:
- Widget component implementations (handled by C008, C009)
- LangGraph server setup (handled by C003)

## 1.3 Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-SD-001 | Frontend MUST use LangGraph SDK (`@langchain/langgraph-sdk-react-ui`) | Must |
| FR-SD-002 | Backend MUST emit widgets via `push_ui_message()` | Must |
| FR-SD-003 | Frontend MUST render widgets via `LoadExternalComponent` | Must |
| FR-SD-004 | Widget names MUST match backend `push_ui_message()` calls | Must |

## 1.4 Acceptance Criteria

- [ ] LangGraph SDK installed
- [ ] useStream() configured
- [ ] LoadExternalComponent renders widgets
- [ ] Widget names match between frontend and backend
