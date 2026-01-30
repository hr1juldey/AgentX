# Specs Artifact: c007-frontend-architecture

**Generated**: 2026-01-29
**Change**: c007-frontend-architecture
**Schema**: spec-factory v1.0.0

---

## 1. Spec: langgraph-server-driven-ui

**File**: `specs/langgraph-server-driven-ui/spec.md`

**Purpose**: Define the LangGraph server-driven UI architecture where the backend has full control over UI rendering.

**Key Requirements**:
- LangGraph SDK installation (`@langchain/langgraph-sdk-react-ui`)
- useStream() hook configuration
- LoadExternalComponent rendering
- Backend widget emission via `push_ui_message()`

**Acceptance Criteria**:
- [ ] LangGraph SDK installed
- [ ] useStream() configured
- [ ] LoadExternalComponent renders widgets

---

## 2. Spec: component-colocation

**File**: `specs/component-colocation/spec.md`

**Purpose**: Define the component colocation strategy where ui.tsx widget registries are placed next to graph.py.

**Key Requirements**:
- ui.tsx placement (same directory as graph.py)
- Widget registry format (default export)
- Absolute import paths

**Acceptance Criteria**:
- [ ] ui.tsx exists next to graph.py
- [ ] Widget registry uses default export

---

## 3. Spec: shadow-dom-isolation

**File**: `specs/shadow-dom-isolation/spec.md`

**Purpose**: Define the Shadow DOM isolation strategy that prevents CSS conflicts.

**Key Requirements**:
- Shadow DOM configuration for LoadExternalComponent
- Style isolation per widget

**Acceptance Criteria**:
- [ ] Shadow DOM configured
- [ ] No CSS bleed between widgets

---

## 4. Spec: ui-message-reducer

**File**: `specs/ui-message-reducer/spec.md`

**Purpose**: Define the ui_message_reducer state management pattern.

**Key Requirements**:
- AgentState includes ui field with ui_message_reducer
- Automatic state tracking

**Acceptance Criteria**:
- [ ] AgentState includes ui field
- [ ] UI state automatically tracked

---

## 5. Spec: widget-protocol

**File**: `specs/widget-protocol/spec.md`

**Purpose**: Define the widget protocol with 12 widget types.

**Key Requirements**:
- 12 widget types defined
- Widget names frozen after Phase 7

**Widget Types**:
- markdown, card, form, progress, action, confirmation, image, gallery, chart, searchResult, hopProgress, citationCard

**Acceptance Criteria**:
- [ ] All 12 widget types defined
- [ ] Widget names frozen

---

## 6. Cross-Domain Contracts

### 6.1 Shared Types

```typescript
// AnyUIMessage (from LangGraph)
type AnyUIMessage = {
  id: string
  name: string  // Widget type
  props: Record<string, any>
  metadata?: Record<string, any>
}

// WidgetType enum
type WidgetType =
  | 'markdown'
  | 'card'
  | 'form'
  | 'progress'
  | 'action'
  | 'confirmation'
  | 'image'
  | 'gallery'
  | 'chart'
  | 'searchResult'
  | 'hopProgress'
  | 'citationCard'
```

### 6.2 Integration Points

| Domain A | Domain B | Interface |
|----------|----------|-----------|
| **langgraph-server-driven-ui** | **component-colocation** | ui.tsx registry with 12 widget types |
| **langgraph-server-driven-ui** | **shadow-dom-isolation** | LoadExternalComponent with Shadow DOM |
| **langgraph-server-driven-ui** | **ui-message-reducer** | State management via ui_message_reducer |
| **ui-message-reducer** | **widget-protocol** | 12 widget types with AnyUIMessage |
| **component-colocation** | **C003 agent-pipeline** | ui.tsx next to graph.py |

### 6.3 Component Registration

```typescript
// src/agent/ui.tsx (colocated with graph.py)
export default {
  markdown: MarkdownComponent,
  card: CardComponent,
  form: FormComponent,
  progress: ProgressComponent,
  action: ActionComponent,
  confirmation: ConfirmationComponent,
  image: ImageComponent,
  gallery: GalleryComponent,
  chart: ChartComponent,
  searchResult: SearchResultComponent,
  hopProgress: HopProgressComponent,
  citationCard: CitationCardComponent,
};
```

---

**Next Artifact**: design.md
