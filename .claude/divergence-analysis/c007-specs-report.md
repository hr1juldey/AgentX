# C007 Frontend Architecture Requirements Report

Based on analysis of archived C007 (frontend-architecture) OpenSpec change.

## 1. Requirements from tasks.md (Implementation Checklist)

### Phase 1: LangGraph SDK Setup (1 hour)

| Task | Command/File | Status | Expected Implementation |
|------|-------------|--------|------------------------|
| Install LangGraph SDK | `npm install @langchain/langgraph-sdk` | ✓ | Package.json includes `@langchain/langgraph-sdk-react-ui v0.0.11` |
| Configure useStream() | `src/hooks/useLangGraph.ts` | ✓ | Custom hook wrapping LangGraph stream with ui_msg_reducer |
| Test connection | `npm run dev` | ⬜ | Integration with backend LangGraph server |

### Phase 2: Component Colocation (1 hour)

| Task | File | Status | Expected Implementation |
|------|------|--------|------------------------|
| Create agent directory | `src/agent/` | ✓ | LangGraph integration directory |
| Create graph.ts | `src/agent/graph.ts` | ✓ | ~110 lines of LangGraph state definition |
| Create ui.tsx | `src/agent/ui.tsx` | ✓ | ~95 lines of widget registry (default export) |
| Register all 12 widgets | `src/agent/ui.tsx` | ✓ | Component map with all 12 widget types |

### Phase 3: Backend Integration (1 hour)

| Task | File | Status | Expected Implementation |
|------|------|--------|------------------------|
| Implement push_ui_message() | Backend (C003) | ✓ | designer.py:114 - Backend widget emission |
| Configure ui_message_reducer | `src/agent/graph.ts` | ✓ | LangGraph state with ui field and reducer |
| Test widget emission | Integration test | ⬜ | End-to-end widget emission test |

### Phase 4: Shadow DOM Setup (30 minutes)

| Task | File | Status | Expected Implementation |
|------|------|--------|------------------------|
| Configure LoadExternalComponent | `src/components/ui/LoadExternalComponent.tsx` | ✓ | Shadow DOM isolated React portal (~200 lines) |
| Test style isolation | Visual inspection | ⬜ | Visual verification of CSS isolation |

### Phase 5: Designer Agent Fix (30 minutes)

| Task | File | Status | Expected Implementation |
|------|------|--------|------------------------|
| Update Designer agent | Backend (C003) | ✓ | designer.py:161 - state awareness |
| Verify no duplicate widgets | Integration test | ⬜ | Check for widget duplication |

## 2. Architectural Requirements from design.md

### Core Architecture Pattern
- **LangGraph Server-Driven UI**: Backend emits React components via `push_ui_message()`
- **Component Colocation**: ui.tsx widget registry next to graph.py
- **Shadow DOM Isolation**: Style isolation per widget to prevent CSS conflicts
- **Automatic State Management**: ui_message_reducer tracks all UI state automatically

### Layer Structure
```
frontend/src/
├── agent/                    # LangGraph integration (colocated)
│   ├── graph.ts             # LangGraph state definition (~110 lines)
│   └── ui.tsx              # Widget registry (~95 lines)
├── components/
│   └── ui/                 # Widget components
│       ├── LoadExternalComponent.tsx  # Shadow DOM portal (~200 lines)
│       └── widgets/         # 12 widget types
└── pages/                   # Next.js pages
```

### 12 Widget Types Required
1. markdown
2. card
3. form
4. progress
5. action
6. confirmation
7. image
8. gallery
9. chart
10. searchResult
11. hopProgress
12. citationCard

## 3. Acceptance Criteria

### Functional Criteria (7 criteria)
| Criterion | Test Method | Expected Result |
|-----------|-------------|-----------------|
| LangGraph SDK installed | Check package.json | `@langchain/langgraph-sdk-react-ui` present |
| useStream() configured | Check code | Hook implemented with ui_msg_reducer |
| LoadExternalComponent renders | Visual inspection | Widgets display in Shadow DOM |
| Component colocation | File structure check | ui.tsx next to graph.py |
| Shadow DOM isolation | Visual inspection | No CSS bleed between widgets |
| State awareness works | Code review | Designer agent checks state.ui |
| 12 widget types work | Integration test | All widgets render correctly |

### Non-Functional Criteria (3 criteria)
| Criterion | Test Method | Expected Result |
|-----------|-------------|-----------------|
| Bundle size | Build + gzip | <50KB increase (LangGraph SDK) |
| Type safety | TypeScript check | 0 type errors |
| Component file size | WC check | All files <100 lines |
