# Tasks Artifact: c007-frontend-architecture

**Generated**: 2026-01-29
**Change**: c007-frontend-architecture
**Schema**: spec-factory v1.0.0

---

## 1. Implementation Checklist

### 1.1 Phase 1: LangGraph SDK Setup (1 hour)

| Task | Command/File | Status | Notes |
|------|-------------|--------|-------|
| Install LangGraph SDK | `npm install @langchain/langgraph-sdk @langchain/langgraph-sdk-react-ui` | ⬜ | Add to package.json |
| Configure useStream() | `src/pages/_app.tsx` or wrapper | ⬜ | Set up LangGraph provider |
| Test connection | `npm run dev` | ⬜ | Verify connection to backend |

### 1.2 Phase 2: Component Colocation (1 hour)

| Task | File | Status | Notes |
|------|------|--------|-------|
| Create agent directory | `src/agent/` | ⬜ | `mkdir -p src/agent` |
| Create graph.ts | `src/agent/graph.ts` | ⬜ | LangGraph state definition (~100 lines) |
| Create ui.tsx | `src/agent/ui.tsx` | ⬜ | Widget registry (~50 lines) |
| Register all 12 widgets | `src/agent/ui.tsx` | ⬜ | Default export with component map |

### 1.3 Phase 3: Backend Integration (1 hour)

| Task | File | Status | Notes |
|------|------|--------|-------|
| Implement push_ui_message() | Backend (C003) | ⬜ | Python function to emit widgets |
| Configure ui_message_reducer | `src/agent/graph.ts` | ⬜ | Add ui field to AgentState |
| Test widget emission | Integration test | ⬜ | Verify widget appears in frontend |

### 1.4 Phase 4: Shadow DOM Setup (30 minutes)

| Task | File | Status | Notes |
|------|------|--------|-------|
| Configure Shadow DOM | `src/pages/_app.tsx` or wrapper | ⬜ | LoadExternalComponent config |
| Test style isolation | Visual inspection | ⬜ | Verify no CSS bleed between widgets |

### 1.5 Phase 5: Designer Agent Fix (30 minutes)

| Task | File | Status | Notes |
|------|------|--------|-------|
| Update Designer agent | Backend (C003) | ⬜ | Check state.ui before emitting |
| Verify no duplicate widgets | Integration test | ⬜ | Designer agent sees existing widgets |

---

## 2. Verification Steps

### 2.1 Code Quality (Frontend)

```bash
# Type check
npx tsc --noEmit

# Lint (ESLint)
npm run lint

# Format (Prettier)
npm run format
```

### 2.2 Integration Tests

```bash
# Test widget emission
# 1. Backend sends push_ui_message("card", {...})
# 2. Frontend receives via useStream()
# 3. LoadExternalComponent renders CardWidget
# 4. Verify card displays correctly
```

---

## 3. Acceptance Criteria

### 3.1 Functional Criteria

| Criterion | Test Method | Expected Result |
|-----------|-------------|-----------------|
| LangGraph SDK installed | Check package.json | @langchain/langgraph-sdk-react-ui present |
| useStream() configured | Check code | useStream() hook used in app |
| LoadExternalComponent renders | Visual inspection | Widgets display correctly |
| Component colocation | File structure check | ui.tsx next to graph.py |
| Shadow DOM isolation | Visual inspection | No CSS bleed between widgets |
| State awareness works | Code review | Designer agent checks state.ui |
| 12 widget types work | Integration test | All widgets render correctly |

### 3.2 Non-Functional Criteria

| Criterion | Test Method | Expected Result |
|-----------|-------------|-----------------|
| Bundle size | Build + gzip | <50KB increase (LangGraph SDK) |
| Type safety | TypeScript check | 0 type errors |
| Component file size | WC check | All files <100 lines |

---

## 4. Definition of Done

C007-frontend-architecture is **complete** when:

- [ ] All 5 phases are implemented (LangGraph SDK, Component Colocation, Backend Integration, Shadow DOM, Designer Agent Fix)
- [ ] All verification steps pass (code quality, integration tests)
- [ ] All functional acceptance criteria are met (7 criteria)
- [ ] All non-functional acceptance criteria are met (3 criteria)
- [ ] Integration test passes (widget emission → rendering)
- [ ] Code review approved
- [ ] Documentation updated (if applicable)

---

## 5. Dependencies Unlocked

This change unlocks:

| Change | Unlocked Feature |
|--------|-----------------|
| **C008-organic-ui** | Visual layer (metaballs, voice nucleus, tokens) |
| **C009-ui-polish** | UI polish (flat design, single accent, spacing tokens) |

---

## 6. Implementation Notes

### 6.1 C003 Dependency

C007 depends on C003 (agent-pipeline) for:
- LangGraph state management (AgentState with ui field)
- ui_message_reducer configuration
- Backend graph execution

**If C003 is not complete**:
- Defer C007 until C003 is complete
- Use mock LangGraph state for testing

---

**End of spec-factory pipeline**

All 7 artifacts complete for C007-frontend-architecture:
1. ✅ scan.md
2. ✅ extract.md
3. ✅ validate.md
4. ✅ proposal.md
5. ✅ specs.md (with 5 spec files)
6. ✅ design.md
7. ✅ tasks.md
