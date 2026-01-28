# Scan Artifact: c007-frontend-architecture

**Generated**: 2026-01-29
**Change**: c007-frontend-architecture
**Schema**: spec-factory v1.0.0

---

## 1. LLD Synthesis

### 1.1 Relevant LLD Documents

| Document | Path | Relevance |
|----------|------|-----------|
| **Domain Model** | `/docs/engineering/lld/domain_model.md` | Entity definitions, repository patterns |
| **Agent Runtime** | `/docs/engineering/lld/agent_runtime.md` | DSPy + LangGraph integration |
| **Incremental Release** | `/docs/engineering/lld/incremental_release_plan.md` | Phase implementation details |

### 1.2 Locked Definitions from LLD

#### Entities
```python
# From domain_model.md - @dataclass pattern
@dataclass
class UIDescriptor:
    descriptor_id: str
    descriptor_type: WidgetType
    title: Optional[str]
    content: Optional[WidgetContent]
    metadata: Dict[str, Any]
```

#### Enums
```python
# Widget types must match frontend
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

#### Signatures (DSPy)
```python
# 7 UI decision signatures for agent pipeline
class SelectWidget(Signature):
    """Select appropriate widget type based on user intent."""
    question = InputField(desc="User's question or intent")
    context = InputField(desc="Available context and data")
    widget_type = OutputField(desc="One of: text, card, form, progress, action, confirmation")
```

#### Repository Interfaces
```python
# ABC pattern from Mimicus
class WidgetRepository(ABC):
    @abstractmethod
    async def save(self, widget: UIDescriptor) -> UIDescriptor:
        pass

    @abstractmethod
    async def find_by_id(self, widget_id: str) -> Optional[UIDescriptor]:
        pass
```

---

## 2. Codebase Exploration (opsx:explore)

### 2.1 Exploration Topics

**Exploration #1: LangGraph Server-Driven UI**
- Source: https://docs.langchain.com/langsmith/generative-ui-react
- Focus: LoadExternalComponent, ui_message_reducer, component colocation

**Exploration #2: R014 Frontend Architecture**
- Source: `/prototypes/R014_ui_showcase/frontend/`
- Focus: Atomic state pattern, widget rendering, WebSocket integration

**Exploration #3: Organic UI Design System**
- Source: `/docs/engineering/agentx_organic_ui_design_system.md`
- Focus: Design tokens, metaball physics, voice nucleus

### 2.2 File Inventory

#### Backend Files (LangGraph Integration)
| File | Lines | Purpose |
|------|-------|---------|
| `langgraph.json` | ~20 | Graph + UI component mapping |
| `src/agent/index.ts` | ~100 | Graph definition with ui_message_reducer |
| `src/agent/ui.tsx` | ~200 | Colocated React components |

#### Frontend Files (R014 Reference)
| File | Lines | Purpose |
|------|-------|---------|
| `app/page.tsx` | 456 | Main application with widget rendering |
| `store/widget-store.ts` | 311 | Atomic state pattern implementation |
| `types/widget-types.ts` | 213 | Type definitions for 12 widget types |
| `components/widgets/direct-widget-renderer.tsx` | 240 | Type-safe widget rendering |
| `components/widgets/isolated-widget.tsx` | 361 | Self-contained widget with atomic state |
| `hooks/use-websocket-generation.ts` | ~150 | WebSocket streaming integration |
| `hooks/use-widget-handlers.ts` | ~100 | Widget interaction handlers |
| `services/position-service.ts` | ~200 | Widget positioning with collision detection |

#### Design System Files (Organic UI)
| File | Lines | Purpose |
|------|-------|---------|
| `docs/engineering/agentx_organic_ui_design_system.md` | 1117 | Complete design system specification |
| `design/tokens.ts` (to create) | ~200 | Design tokens (colors, spacing, timing) |
| `design/motion.ts` (to create) | ~150 | Motion presets (mitosis, pulse, drift) |
| `design/surfaces.tsx` (to create) | ~100 | Primitive components (Cell, Nucleus) |

---

## 3. Patterns Discovered

### 3.1 Architectural Patterns

#### LangGraph Server-Driven UI Pattern
```
┌─────────────────────────────────────────────────────────────┐
│                   src/agent/                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  index.ts  ←  Graph definition (StateGraph)         │   │
│  │     AgentState includes ui: Annotated[...]          │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  ui.tsx  ←  React components (colocated!)           │   │
│  │     export default {                                │   │
│  │       weather: WeatherComponent,                    │   │
│  │       writer: WriterComponent,                      │   │
│  │     }                                               │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

**Key Features**:
- Components colocated with graph code
- LangSmith auto-bundles and serves components
- Shadow DOM for style isolation
- ui_message_reducer for state management

#### R014 Atomic State Pattern
```typescript
// Problem: 100+ widgets → cascade re-renders
// Solution: Each widget gets separate Zustand slices

widget_123_data: UIDescriptor
widget_123_viewState: ViewState
widget_123_position: Position
widgetIds: string[]  // Registry

// Usage: Subscribe only to specific slice
const data = useWidgetSlice<UIDescriptor>(`${id}_data`)
```

#### Component Colocation Strategy
```
Backend (LangGraph):
├── src/agent/
│   ├── index.ts       # Graph definition
│   ├── ui.tsx         # Widget components
│   └── widgets/       # Individual widget files
│       ├── MarkdownWidget.tsx
│       ├── CardWidget.tsx
│       └── ...

Frontend (React):
├── app/page.tsx       # useStream + LoadExternalComponent
├── design/            # Organic UI layer (visual skin)
│   ├── tokens.ts
│   ├── motion.ts
│   └── surfaces.tsx
```

### 3.2 Code Patterns

#### Backend Pattern (Python - LangGraph)
```python
from langgraph.graph.ui import AnyUIMessage, ui_message_reducer, push_ui_message

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    ui: Annotated[Sequence[AnyUIMessage], ui_message_reducer]

async def designer_node(state: AgentState):
    existing_widgets = [msg.name for msg in state.ui]  # State awareness!
    push_ui_message("card", {"title": "..."}, message=message)
    return {"messages": [message]}
```

#### Frontend Pattern (TypeScript - LangGraph SDK)
```tsx
import { useStream } from "@langchain/langgraph-sdk/react";
import { LoadExternalComponent } from "@langchain/langgraph-sdk/react-ui";

const { thread, values } = useStream({
  apiUrl: "http://localhost:2024",
  assistantId: "agent",
  onCustomEvent: (event, options) => {
    options.mutate((prev) => {
      const ui = uiMessageReducer(prev.ui ?? [], event);
      return { ...prev, ui };
    });
  },
});

{values.ui?.map((ui) => (
  <LoadExternalComponent key={ui.id} stream={thread} message={ui} />
))}
```

#### Streaming with Merge Pattern
```python
# Backend: Stream updates to same UI message
ui_message = push_ui_message("writer", {"title": "..."}, message=message)
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

### 3.3 Anti-Patterns to Avoid

#### From R014 Postmortem
1. ❌ **Nested callback functions** - Can't test independently
2. ❌ **Bare except: pass** - Hides errors
3. ❌ **Timestamp-based IDs** - Use UUID instead
4. ❌ **Creating Predict instances repeatedly** - Cache them
5. ❌ **Hardcoded metadata values** - Should be dynamic

#### From Design Analysis
1. ❌ **Gradient headers** (R014 chart widget) - Use flat like markdown
2. ❌ **Inconsistent icon colors** (green/gray/blue mix) - Single accent color
3. ❌ **Dev console clutter** - Improve contrast, simplify tabs

---

## 4. Reference Analysis

### 4.1 Mimicus Patterns (Copy Concepts, Not Names)

| Concept | Mimicus Pattern | Intended Use |
|---------|-----------------|--------------|
| Clean Architecture | core/, domain/, application/, infrastructure/, presentation/ | Layer separation |
| Repository | ABC base class + implementations | Data access abstraction |
| Entity | @dataclass with business methods | Core business objects |
| Use Case | Single-purpose classes with execute() | Application logic |
| DTO | Pydantic models for API layer | Request/response validation |

### 4.2 R014 Reference (Concepts Only)

| Concept | R014 Approach | Improved Approach (LangGraph) |
|---------|---------------|-------------------------------|
| **State Management** | Zustand atomic slices (manual) | ui_message_reducer (automatic) |
| **Widget Delivery** | WebSocket + UIDescriptor (data only) | LoadExternalComponent (code + data) |
| **Callbacks** | Nested functions (hard to test) | State-based (testable, traceable) |
| **Component Location** | Frontend only | Colocated with graph |
| **Style Isolation** | Global CSS | Shadow DOM (guaranteed) |
| **Designer Agent** | No state awareness (repeated widgets) | state.ui tracks all shown widgets |

### 4.3 Organic UI Integration

**Decision**: Organic UI as visual skin layer (not widget delivery)

```
┌─────────────────────────────────┐
│   LangGraph Server-Driven UI    │  ← Widget delivery
│   (LoadExternalComponent)       │
└─────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│   Organic UI Visual Layer       │  ← Aesthetics only
│   (Metaballs + Voice Nucleus)   │
└─────────────────────────────────┘
```

**Design Tokens** (from agentx_organic_ui_design_system.md):
```typescript
color: {
  void: '#0A0A0A',           // Deep space background
  membrane: '#141414',        // Primary surface
  enzyme: '#00D9FF',         // Cyan accent
}

metaball: {
  mobileBlur: 12,            // Desktop: 16
  mobileMaxBlobs: 6,         // Desktop: 12
  radius: {
    voice: 160,              // Desktop nucleus
    voiceMobile: 72,         // Mobile nucleus
  }
}
```

---

## 5. Key Files for This Change

### Backend Files (to create/modify)
```
/home/riju279/Documents/Code/XRIG/AgentX/
├── src/agent/
│   ├── __init__.py
│   ├── graph.py              # LangGraph StateGraph with ui_message_reducer
│   ├── nodes/
│   │   ├── analyst.py        # Query understanding
│   │   ├── researcher.py     # Web search
│   │   ├── contextualizer.py # Rerank + filter
│   │   └── designer.py       # UI widget selection (with state awareness!)
│   └── ui/
│       ├── __init__.py
│       └── components.py     # Widget components (colocated)
├── langgraph.json            # Graph + UI mapping
└── domain/
    └── entities/
        └── ui_descriptor.py  # UIDescriptor @dataclass
```

### Frontend Files (to create/modify)
```
/home/riju279/Documents/Code/XRIG/AgentX/
├── app/
│   ├── page.tsx              # useStream + LoadExternalComponent
│   └── layout.tsx            # Root layout
├── design/                   # Organic UI visual layer
│   ├── tokens.ts             # Design tokens
│   ├── motion.ts             # Motion presets
│   └── surfaces.tsx          # Primitives (Cell, Nucleus)
└── components/
    ├── metaball-canvas.tsx  # SVG goo filter
    └── voice-button.tsx      # Central nucleus
```

### Reference Files (read-only)
```
/home/riju279/Documents/Code/XRIG/AgentX/
├── prototypes/R014_ui_showcase/frontend/
│   ├── types/widget-types.ts          # Type definitions reference
│   ├── components/widgets/direct-widget-renderer.tsx  # Widget patterns
│   └── hooks/use-websocket-generation.ts  # WebSocket patterns
├── docs/engineering/
│   └── agentx_organic_ui_design_system.md  # Design tokens reference
└── docs/research/
    └── 02_dspy_mem0_integration.md    # DSPy patterns
```

---

## 6. Integration Points

### Dependencies (from openspec list)
- **C001**: folder-structure (must complete first)
- **C002**: data-contracts (Pydantic v2 ↔ Zod alignment)

### Dependencies for Other Changes
- **C008**: organic-ui (depends on C007 for base architecture)
- **C009**: ui-polish (depends on C007 + C008 for complete system)

### External Dependencies
**Backend (Python)**:
```bash
pip install langgraph langgraph-openai
```

**Frontend (TypeScript)**:
```bash
npm install @langchain/langgraph-sdk @langchain/langgraph-sdk-react-ui
npm install framer-motion  # For Organic UI animations
```

---

## 7. Migration Strategy: R014 → LangGraph

### Phase 1: State Management
```python
# Before (R014 - Zustand):
widget_store = {
  widget_123_data: UIDescriptor,
  widget_123_viewState: ViewState,
}

# After (LangGraph - ui_message_reducer):
class AgentState(TypedDict):
    ui: Annotated[Sequence[AnyUIMessage], ui_message_reducer]
```

### Phase 2: Widget Rendering
```tsx
// Before (R014 - descriptor-based):
<DirectWidgetRenderer descriptor={descriptor} />

// After (LangGraph - server-driven):
<LoadExternalComponent stream={thread} message={ui} />
```

### Phase 3: Designer Agent Fix
```python
# Before (R014 - no state awareness):
# Designer sends same widgets repeatedly

# After (LangGraph - state awareness):
async def designer_node(state: AgentState):
    existing_widgets = [msg.name for msg in state.ui]
    # Designer can now avoid repeating widgets
```

---

**Next Artifact**: extract.md
