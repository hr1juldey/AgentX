# Extract Artifact: c007-frontend-architecture

**Generated**: 2026-01-29
**Change**: c007-frontend-architecture
**Schema**: spec-factory v1.0.0

---

## 1. Pattern Catalog

### 1.1 Architectural Patterns

| Pattern | Source | Description | Apply? |
|---------|--------|-------------|--------|
| **Server-Driven UI** | LangGraph | Components colocated with graph code, bundled and served | ✅ **Critical** |
| **Shadow DOM Isolation** | LangGraph | Style isolation via shadow DOM | ✅ **Critical** |
| **ui_message_reducer** | LangGraph | State management for UI messages | ✅ **Critical** |
| **Component Colocation** | LangGraph | ui.tsx next to index.ts | ✅ **Critical** |
| **Clean Architecture** | mimicus | Layered separation with domain independence | ✅ |
| **Repository Pattern** | mimicus | ABC base + implementations | ✅ |
| **DTO Pattern** | mimicus | Pydantic models for API layer | ✅ |
| **Atomic State Pattern** | R014 | Separate Zustand slices per widget | ❌ Use LangGraph state instead |
| **LoadExternalComponent** | LangGraph | Fetch and render bundled components | ✅ **Critical** |

### 1.2 Code Structure Patterns

| Pattern | Example | Apply? |
|---------|---------|--------|
| **@dataclass entities** | `class AgentSessionEntity:` | ✅ |
| **ABC repositories** | `class AgentSessionRepository(ABC):` | ✅ |
| **Static mappers** | `@staticmethod def to_dto()` | ✅ |
| **Use case classes** | `class CreateSessionUseCase:` | ✅ |
| **Singleton DI** | `get_use_case()` pattern | ✅ |
| **Component colocation** | `src/agent/ui.tsx` with `index.ts` | ✅ |
| **Typed UI emission** | `typedUi<typeof ComponentMap>(config)` | ✅ |

### 1.3 Naming Patterns (to Avoid from R014)

| R014 Name | Why Avoid | Alternative |
|-----------|-----------|-------------|
| **Nested callbacks** | `widget_callback=send_widget` | Use `ui_message_reducer` + `push_ui_message()` |
| **Timestamp-based IDs** | `id=f"widget-{datetime.now().timestamp()}"` | Use `uuid.uuid4()` or `uuidv4()` |
| **Hardcoded metadata** | `"button_text": "Confirm"` | Generate from LLM or pass as props |
| **Predict in loops** | `dspy.Predict()`) in each call | Cache Predict instances |
| **Descriptor-only UI** | WebSocket sends only data | Server-driven UI sends code + data |
| **Gradient headers** | Chart widget has gradient | Use flat design (no gradients) |
| **Mixed icon colors** | Green/gray/blue icons | Single accent color (enzyme: #00D9FF) |
| **Absolute imports** | Already enforced in CLAUDE_POLICY.md | Keep using absolute imports |

---

## 2. Specification Drafts

### 2.1 Draft: Frontend Architecture Spec

**Purpose**: Define LangGraph server-driven UI architecture for Real AgentX

**Scope**:
- **In scope**: LangGraph SDK integration, component colocation, state management, WebSocket streaming
- **Out of scope**: Organic UI visual layer (C008), aesthetic polish (C009), backend DSPy logic (C003)

**Locked from LLD**:
```python
# From domain_model.md
@dataclass
class UIDescriptor:
    descriptor_id: str
    descriptor_type: WidgetType
    title: Optional[str]
    content: Optional[WidgetContent]
    metadata: Dict[str, Any]

# From agent_runtime.md
class WidgetType(str, Enum):
    MARKDOWN = "markdown"
    CARD = "card"
    FORM = "form"
    PROGRESS = "progress"
    ACTION = "action"
    CONFIRMATION = "confirmation"
    IMAGE = "image"
    GALLERY = "gallery"
    CHART = "chart"
```

**Requirements**:
1. Components must be colocated with graph code (`src/agent/ui.tsx`)
2. Use `ui_message_reducer` for UI state management
3. Use `LoadExternalComponent` for rendering
4. Use `push_ui_message()` to emit UI from backend nodes
5. Support streaming updates with `merge=True` pattern
6. Shadow DOM for style isolation
7. Designer agent has state awareness (can see existing widgets)

**Acceptance Criteria**:
- [ ] Frontend can receive and render server-driven UI components
- [ ] Backend nodes can emit UI with `push_ui_message()`
- [ ] UI state tracked via `ui_message_reducer`
- [ ] Streaming updates work with `merge=True`
- [ ] Shadow DOM prevents style conflicts
- [ ] Designer agent avoids repeating widgets

### 2.2 Draft: Component Protocol Spec

**Purpose**: Define backend-frontend component communication protocol

**Scope**:
- **In scope**: Component registration, props passing, message association
- **Out of scope**: Component implementation details, styling

**Locked from LLD**:
```python
# DSPy signature for widget selection
class SelectWidget(Signature):
    """Select appropriate widget type based on user intent."""
    question = InputField(desc="User's question or intent")
    context = InputField(desc="Available context and data")
    widget_type = OutputField(desc="One of: text, card, form, progress, action, confirmation")
```

**Requirements**:
1. Components registered in `langgraph.json` under `ui` section
2. Component names map to backend widget types
3. Props passed from backend must match component TypeScript interface
4. UI messages associated with AIMessage for conversation context
5. Namespace customization supported for multi-graph setups

**Component Registration Schema**:
```json
{
  "ui": {
    "agent": "./src/agent/ui.tsx"
  }
}
```

**Component Export Schema**:
```typescript
export default {
  markdown: MarkdownComponent,
  card: CardComponent,
  form: FormComponent,
  // ... 12 widget types total
};
```

**Acceptance Criteria**:
- [ ] Components registered in `langgraph.json`
- [ ] Backend can emit UI by component name
- [ ] Frontend loads and renders correct component
- [ ] Props type-safe between backend and frontend
- [ ] Message association works correctly

### 2.3 Draft: Streaming Protocol Spec

**Purpose**: Define real-time UI update streaming protocol

**Scope**:
- **In scope**: UI message streaming, merge updates, event handling
- **Out of scope**: LLM token streaming (separate protocol)

**Requirements**:
1. Frontend uses `onCustomEvent` callback to receive UI updates
2. Backend sends updates with same UI message ID + `merge=True`
3. Frontend uses `ui_message_reducer` to merge updates into state
4. Progressive updates during LLM generation (e.g., content streaming)

**Backend Pattern**:
```python
ui_message = push_ui_message("writer", {"title": "..."}), message=message)
ui_message_id = ui_message["id"]

for chunk in content_stream:
    push_ui_message(
        "writer",
        {"content": chunk.text},
        id=ui_message_id,  # Same ID!
        merge=True,        # Merge props!
        message=message,
    )
```

**Frontend Pattern**:
```typescript
onCustomEvent: (event, options) => {
  options.mutate((prev) => {
    const ui = uiMessageReducer(prev.ui ?? [], event);
    return { ...prev, ui };
  });
}
```

**Acceptance Criteria**:
- [ ] UI updates stream in real-time
- [ ] Multiple updates merge into single UI message
- [ ] Component re-renders with merged props
- [ ] No duplicate UI messages created

---

## 3. API Contracts

### 3.1 REST Endpoints

| Method | Path | Request | Response |
|--------|------|---------|----------|
| **POST** | `/runs` | `{"thread_id": str, "assistant_id": str}` | `{"run_id": str, "thread_id": str}` |
| **GET** | `/runs/{run_id}/stream` | - | Server-Sent Events stream |
| **GET** | `/threads/{thread_id}` | - | `{"thread_id": str, "values": State}` |

**Note**: REST endpoints used by LangGraph SDK `useStream()` hook.

### 3.2 WebSocket Channels

| Channel | Direction | Message Schema |
|---------|-----------|----------------|
| **custom_events** | Backend → Frontend | `AnyUIMessage` (UI updates) |
| **messages** | Bidirectional | `BaseMessage` (chat messages) |

**Event Schema**:
```python
class AnyUIMessage(TypedDict):
    id: str
    name: str  # Component name
    props: Dict[str, Any]
    metadata: Dict[str, Any]
    # Optional merge fields
    merge: Optional[bool]
```

### 3.3 Port Assignments

| Service | Port | Purpose |
|---------|------|---------|
| **LangGraph Server** | 2024 | Main agent server (from LangGraph docs) |
| **Frontend Dev** | 3000 | Next.js dev server |
| **Voice API** | 8015 | Audio streaming (from C004) |
| **Search API** | 8016 | Web search service |

**Note**: LangGraph default port is 2024, avoids 8000-8014 range per constraints.

---

## 4. Data Model Mappings

### 4.1 Pydantic → Zod Mappings

| Pydantic Model | Zod Type | Notes |
|----------------|----------|-------|
| **UIDescriptor** | `UIDescriptorSchema` | Core widget descriptor |
| **WidgetType** | `WidgetTypeSchema` | Enum: 12 widget types |
| **SearchRequest** | `SearchRequestSchema` | Search input |
| **FormRequest** | `FormRequestSchema` | Form data |

**Backend (Pydantic v2)**:
```python
from pydantic import BaseModel

class UIDescriptor(BaseModel):
    descriptor_id: str
    descriptor_type: WidgetType
    title: str | None = None
    content: str | dict | None = None
    metadata: dict[str, Any] = {}
```

**Frontend (Zod)**:
```typescript
import { z } from 'zod';

export const UIDescriptorSchema = z.object({
  descriptor_id: z.string(),
  descriptor_type: WidgetTypeSchema,
  title: z.string().optional(),
  content: z.union([z.string(), z.record(z.unknown())]).optional(),
  metadata: z.record(z.unknown()).optional(),
});
```

### 4.2 Shared Types

**WidgetType Enum** (Must match exactly):
```python
# Backend (Python)
class WidgetType(str, Enum):
    MARKDOWN = "markdown"
    CARD = "card"
    FORM = "form"
    PROGRESS = "progress"
    ACTION = "action"
    CONFIRMATION = "confirmation"
    IMAGE = "image"
    GALLERY = "gallery"
    CHART = "chart"
    SEARCH_RESULT = "search-result"
    HOP_PROGRESS = "hop-progress"
    CITATION_CARD = "citation-card"
```

```typescript
// Frontend (TypeScript + Zod)
export const WidgetTypeSchema = z.enum([
  "markdown",
  "card",
  "form",
  "progress",
  "action",
  "confirmation",
  "image",
  "gallery",
  "chart",
  "search-result",
  "hop-progress",
  "citation-card",
]);

export type WidgetType = z.infer<typeof WidgetTypeSchema>;
```

### 4.3 Component Props Mappings

| Component | Props Schema | Source |
|-----------|--------------|--------|
| **MarkdownComponent** | `{ content: string }` | R014 `MarkdownWidget` |
| **CardComponent** | `{ title: string, content: string }` | R014 `CardWidget` |
| **FormComponent** | `{ title: string, fields: FormField[] }` | R014 `FormWidget` |
| **ProgressComponent** | `{ task_name: string, progress: number }` | R014 `ProgressWidget` |
| **ActionComponent** | `{ button_text: string, action_id: string }` | R014 `ActionWidget` |
| **ConfirmationComponent** | `{ title: string, message: string }` | R014 `ConfirmationWidget` |

---

## 5. Dependencies on Other Specs

| Spec | Dependency Type | Rationale |
|------|-----------------|-----------|
| **C001: folder-structure** | **Hard** | File organization must exist before components |
| **C002: data-contracts** | **Hard** | Pydantic ↔ Zod alignment must be complete |
| **C003: agent-pipeline** | **Soft** | Backend nodes emit UI, but can work independently |
| **C008: organic-ui** | **Dependent** | Depends on C007 for base architecture |
| **C009: ui-polish** | **Dependent** | Depends on C007 + C008 for complete system |

**Dependency Graph**:
```
C001 (folder-structure)
  ↓
C002 (data-contracts)
  ↓
C007 (frontend-architecture) ← YOU ARE HERE
  ↓
C008 (organic-ui)
  ↓
C009 (ui-polish)

C003 (agent-pipeline) ← Can proceed in parallel
```

---

## 6. File Structure Template

### Backend Structure
```
src/
├── agent/
│   ├── __init__.py
│   ├── graph.py              # StateGraph with ui_message_reducer
│   ├── state.py              # AgentState TypedDict
│   ├── nodes/
│   │   ├── __init__.py
│   │   ├── analyst.py        # Query understanding
│   │   ├── designer.py       # UI widget selection (with state awareness!)
│   │   └── ...
│   └── ui/
│       ├── __init__.py
│       └── components.py     # Widget components (colocated)
└── langgraph.json            # Graph + UI mapping
```

### Frontend Structure
```
app/
├── page.tsx                  # useStream + LoadExternalComponent
└── layout.tsx                # Root layout

components/
├── metaball-canvas.tsx      # SVG goo filter (C008)
└── voice-button.tsx          # Central nucleus (C008)

design/                         # Organic UI layer (C008)
├── tokens.ts
├── motion.ts
└── surfaces.tsx
```

---

## 7. Integration Checklist

### Backend Setup
- [ ] Install LangGraph: `pip install langgraph langgraph-openai`
- [ ] Create `langgraph.json` with `ui` section
- [ ] Define `AgentState` with `ui_message_reducer`
- [ ] Implement `designer_node` with state awareness
- [ ] Colocate components in `src/agent/ui.py`
- [ ] Register components in `langgraph.json`

### Frontend Setup
- [ ] Install LangGraph SDK: `npm install @langchain/langgraph-sdk @langchain/langgraph-sdk-react-ui`
- [ ] Set up `useStream()` hook with `onCustomEvent`
- [ ] Implement `<LoadExternalComponent>` rendering
- [ ] Add `ui_message_reducer` to state mutations
- [ ] Test component loading and rendering
- [ ] Verify streaming updates work

### Migration from R014
- [ ] Remove Zustand atomic state (replace with LangGraph state)
- [ ] Remove descriptor-only WebSocket pattern
- [ ] Remove nested callback functions
- [ ] Add Shadow DOM wrapper
- [ ] Update Designer agent to use `state.ui`

---

**Next Artifact**: validate.md
