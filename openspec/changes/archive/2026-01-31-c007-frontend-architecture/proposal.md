# Proposal: c007-frontend-architecture

**Generated**: 2026-01-29
**Change**: c007-frontend-architecture
**Schema**: spec-factory v1.0.0

---

## Summary

Implement the LangGraph server-driven UI architecture for AgentX v0.1, featuring component colocation, Shadow DOM isolation, and ui_message_reducer state management. This replaces R014's callback-based pattern with a state-based approach where the backend has full control over UI rendering.

---

## Motivation

### Problem Statement

R014 UI showcase has architectural issues that limit scalability and state awareness:
1. **Nested callbacks** make state tracking difficult (no awareness of existing UI)
2. **Descriptor-only WebSocket** sends only data, not components (limited flexibility)
3. **Designer agent problem**: Sends same widgets repeatedly because it can't see existing UI state
4. **Tight coupling**: Widget names hardcoded in frontend, can't evolve independently

### Current State

R014 UI showcase provides:
- Callback-based widget delivery (widget_callback, qa_callback)
- Descriptor-only WebSocket (JSON data only)
- Atomic state pattern with Zustand (separate slices per widget)
- Hardcoded widget names in frontend

### Desired State

C007 Frontend Architecture delivers:
- **Server-driven UI**: Backend sends React components via `push_ui_message()`
- **State awareness**: `ui_message_reducer` tracks all UI state in `state.ui`
- **Component colocation**: ui.tsx placed next to graph.py in backend code
- **Shadow DOM isolation**: Each widget isolated from global CSS
- **LangGraph SDK**: Industry-standard library for server-driven UI

---

## Scope

### In Scope

- LangGraph SDK integration (frontend: `@langchain/langgraph-sdk-react-ui`)
- Component colocation (ui.tsx next to graph.py)
- Shadow DOM isolation (style isolation per widget)
- ui_message_reducer (state management for UI messages)
- push_ui_message() (backend API for emitting widgets)
- LoadExternalComponent (frontend rendering)
- 12 widget types (markdown, card, form, progress, action, confirmation, image, gallery, chart, searchResult, hopProgress, citationCard)

### Out of Scope

- Widget component implementations (handled by C008 organic-ui, C009 ui-polish)
- LangGraph server setup (handled by C003 agent-pipeline)
- Voice WebSocket (handled by C004 voice-streaming)
- Backend API endpoints (handled by C001-C006)

### Dependencies

| Change | Status | Required For |
|--------|--------|--------------|
| **C001-folder-structure** | Done | Frontend folder structure |
| **C002-data-contracts** | Done | Pydantic ↔ Zod alignment |
| **C003-agent-pipeline** | Done | LangGraph state management, ui_message_reducer |

---

## Success Criteria

1. **Server-driven UI works**: Backend emits widgets, frontend renders via LoadExternalComponent
   - Measure: Integration test (send widget, verify rendering)
   - Target: Widget displays correctly

2. **State awareness works**: Designer agent can see existing UI state
   - Measure: Code review (check `state.ui` usage)
   - Target: Designer agent checks existing widgets before emitting new ones

3. **Component colocation implemented**: ui.tsx next to graph.py
   - Measure: File structure check
   - Target: ui.tsx exists in same directory as graph.py

4. **Shadow DOM isolation**: Each widget isolated from global CSS
   - Measure: Visual inspection (check CSS bleed)
   - Target: No CSS conflicts between widgets

5. **12 widget types supported**: All widget types render correctly
   - Measure: Integration test (each widget type)
   - Target: All 12 widgets display correctly

---

## Implementation Approach

### High-Level Approach

**Phase 1: LangGraph SDK Setup** (1 hour)
- Install LangGraph SDK: `npm install @langchain/langgraph-sdk @langchain/langgraph-sdk-react-ui`
- Configure useStream() hook
- Set up LoadExternalComponent

**Phase 2: Component Colocation** (1 hour)
- Create ui.tsx registry files
- Place ui.tsx next to graph.py
- Register all 12 widget types

**Phase 3: Backend Integration** (1 hour)
- Implement push_ui_message() in backend
- Configure ui_message_reducer in LangGraph state
- Test widget emission

**Phase 4: Shadow DOM Setup** (30 minutes)
- Configure Shadow DOM for LoadExternalComponent
- Test style isolation

**Phase 5: Designer Agent Fix** (30 minutes)
- Update Designer agent to check state.ui
- Verify no duplicate widgets

### Key Decisions

| Decision | Rationale | Alternatives Considered |
|----------|-----------|------------------------|
| **Server-driven UI over descriptor-only** | Backend has full control (code + data), Designer agent gets state awareness | Descriptor-only (limited flexibility, no state awareness) |
| **Component colocation** | Industry standard (LangSmith), easier to maintain | Separate UI directory (harder to maintain, no colocation benefit) |
| **Shadow DOM isolation** | Prevents CSS conflicts between widgets | CSS modules (more complex, doesn't prevent all conflicts) |
| **ui_message_reducer** | Automatic state tracking, no manual state management needed | Manual state management (error-prone, complex) |
| **LangGraph SDK** | Industry standard, well-documented, production-ready | Custom WebSocket implementation (reinventing wheel) |

### Constraints

- **Ports**: Frontend port 3000 (from C007 setup)
- **File size**: Max 100 lines per component file
- **Imports**: Absolute imports only (`@/agent/ui`, `@/components`)
- **Dependencies**: Must wait for C003 (LangGraph setup)

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **LangGraph SDK compatibility** | Low | Medium | Use documented patterns, check version compatibility |
| **Bundle size increase** | Medium | Medium | Tree-shake unused imports, monitor bundle size |
| **Shadow DOM performance** | Low | Low | Shadow DOM is well-optimized in modern browsers |
| **Designer agent complexity** | Medium | Low | state.ui makes state tracking simple |
| **Widget naming conflicts** | Low | Low | Centralized registry in ui.tsx prevents conflicts |

---

## Open Questions

1. **Bundle size impact**: How much will LangGraph SDK add to bundle?
   - **Recommendation**: Monitor bundle size during implementation, target <50KB increase
   - **Decision point**: During implementation (build step)

2. **Shadow DOM browser support**: Do we need a fallback for older browsers?
   - **Recommendation**: No, Shadow DOM is supported in all modern browsers (Chrome 90+, Safari 14+, Firefox 88+, Edge 90+)
   - **Decision point**: During implementation (browser compatibility check)

---

**Next Artifact**: specs.md
