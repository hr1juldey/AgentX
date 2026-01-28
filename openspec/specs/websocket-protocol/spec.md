# Spec: websocket-protocol

**File**: `specs/websocket-protocol/spec.md`

## 1.1 Purpose

Define the LangGraph server-driven UI protocol using `ui_message_reducer` for state management and `push_ui_message()` for backend emission, replacing the R014 descriptor-only WebSocket pattern.

## 1.2 Scope

**In Scope**:
- LangGraph SDK `useStream()` hook integration
- `onCustomEvent` callback for UI updates
- `ui_message_reducer` for state management
- `push_ui_message()` backend API
- Streaming updates with `merge=True` pattern
- Component colocation (ui.tsx with graph.py)
- Shadow DOM for style isolation

**Out of Scope**:
- UI descriptor contracts (see ui-descriptor-contracts spec)
- Pydantic ↔ Zod sync (see pydantic-zod-sync spec)
- LangGraph StateGraph definition (see C003-agent-pipeline)

## 1.3 Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-WS-001 | Frontend SHALL use LangGraph SDK `useStream()` hook | Must |
| FR-WS-002 | Frontend SHALL use `onCustomEvent` callback for UI updates | Must |
| FR-WS-003 | Frontend SHALL use `ui_message_reducer` for state updates | Must |
| FR-WS-004 | Backend SHALL use `push_ui_message()` to emit UI | Must |
| FR-WS-005 | Backend nodes SHALL access `state.ui` for state awareness | Must |
| FR-WS-006 | Streaming updates SHALL use `merge=True` with same message ID | Must |
| FR-WS-007 | Components SHALL use `LoadExternalComponent` for rendering | Must |
| FR-WS-008 | Components SHALL be colocated with graph code (ui.tsx) | Must |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-WS-001 | Real-time UI updates < 100ms latency | Should |
| NFR-WS-002 | State synchronization guaranteed | Must |
| NFR-WS-003 | Shadow DOM prevents style conflicts | Must |
| NFR-WS-004 | Component bundling via LangSmith | Must |

## 1.4 Data Model

### AgentState (Backend)

```python
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph.ui import AnyUIMessage, ui_message_reducer

class AgentState(TypedDict):
    """Agent state with UI message tracking."""
    messages: Annotated[Sequence[BaseMessage], add_messages]
    ui: Annotated[Sequence[AnyUIMessage], ui_message_reducer]
    # ^ ui_message_reducer automatically manages UI state
```

### AnyUIMessage Structure

```python
from typing import Any, Dict

class AnyUIMessage(TypedDict):
    """UI message emitted from backend to frontend."""
    id: str  # Unique message ID (use uuid.uuid4())
    name: str  # Component name (must match ui.tsx export)
    props: Dict[str, Any]  # Component props (must match TypeScript interface)
    metadata: Dict[str, Any]  # Optional metadata
    # Streaming fields (optional):
    merge: Optional[bool] = None  # True to merge with existing message
```

### ThreadState (Frontend)

```typescript
interface ThreadState {
  ui: AnyUIMessage[];  // Managed by ui_message_reducer
  messages: BaseMessage[];
  // ... other state
}
```

## 1.5 API Contract

### Backend Emission Pattern

```python
from langgraph.graph.ui import push_ui_message
from uuid import uuid4

async def designer_node(state: AgentState):
    """Designer node with state awareness."""
    # Check existing widgets (state awareness!)
    existing_widgets = [msg.name for msg in state.ui]

    # Emit UI message
    push_ui_message(
        "card",  # Component name (must match ui.tsx export)
        {
            "title": "Search Results",
            "content": "Found 5 results...",
            "metadata": {"count": 5}
        },
        message=message  # Associate with AIMessage for context
    )

    return {"messages": [message]}
```

### Streaming with Merge Pattern

```python
async def writer_node(state: AgentState):
    """Stream content updates to same UI message."""
    # Create initial UI message
    ui_message = push_ui_message(
        "writer",
        {"title": "Generating response..."},
        message=message
    )
    ui_message_id = ui_message["id"]

    # Stream updates (merge props)
    for chunk in content_stream:
        push_ui_message(
            "writer",
            {"content": chunk.text},  # New content
            id=ui_message_id,  # Same ID!
            merge=True,  # Merge props!
            message=message,
        )

    return {"messages": [message]}
```

### Frontend Integration Pattern

```tsx
import { useStream } from "@langchain/langgraph-sdk/react";
import { LoadExternalComponent } from "@langchain/langgraph-sdk/react-ui";
import { uiMessageReducer } from "@langchain/langgraph-sdk/react";

function AgentPage() {
  const { thread, values } = useStream({
    apiUrl: "http://localhost:2024",
    assistantId: "agent",
    onCustomEvent: (event, options) => {
      // Update UI state with ui_message_reducer
      options.mutate((prev) => {
        const ui = uiMessageReducer(prev.ui ?? [], event);
        return { ...prev, ui };
      });
    },
  });

  return (
    <div>
      {values.ui?.map((ui) => (
        <LoadExternalComponent
          key={ui.id}
          stream={thread}
          message={ui}
          fallback={<SkeletonWidget />}
        />
      ))}
    </div>
  );
}
```

### Component Registration (langgraph.json)

```json
{
  "graphs": {
    "agent": "./agent/graph.py"
  },
  "ui": {
    "agent": "./agent/ui.tsx"
  }
}
```

### Component Export (ui.tsx)

```typescript
// agent/ui.tsx (colocated with graph.py)
import { CardComponent } from "./widgets/CardWidget";
import { MarkdownComponent } from "./widgets/MarkdownWidget";
// ... import all 12 widget types

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

## 1.6 Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-WS-001 | Component names must match ui.tsx export exactly | Code review, load error would fail |
| BR-WS-002 | Use uuid.uuid4() for message IDs (not timestamp) | Code review |
| BR-WS-003 | Designer agent checks state.ui before emitting | Code review |
| BR-WS-004 | Use same ID for streaming updates with merge=True | Code review |
| BR-WS-005 | Components use Shadow DOM for style isolation | LoadExternalComponent wrapper |

## 1.7 Acceptance Criteria

- [ ] Frontend uses `useStream()` hook with `onCustomEvent`
- [ ] Frontend uses `ui_message_reducer` for state updates
- [ ] Backend nodes use `push_ui_message()` to emit UI
- [ ] Backend nodes access `state.ui` for state awareness
- [ ] Streaming updates use `merge=True` with same message ID
- [ ] Components rendered via `LoadExternalComponent`
- [ ] Components colocated in agent/ui.tsx
- [ ] Shadow DOM prevents style conflicts
- [ ] LangGraph server on port 2024

## 1.8 Message Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    LangGraph Server-Driven UI Flow              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Backend (LangGraph)         Frontend (Next.js)                 │
│  ┌──────────────────┐        ┌──────────────────┐              │
│  │ designer_node()  │        │ useStream()      │              │
│  │                  │        │                  │              │
│  │ state.ui = [...] │─┐      │ onCustomEvent()  │              │
│  │                  │ │      │                  │              │
│  │ push_ui_message( │ │      │ uiMessageReducer │              │
│  │   "card",        │ │      │   (prev.ui, event│              │
│  │   {...}          │ │      │    )             │              │
│  │ )                │ │      │                  │              │
│  └──────────────────┘ │      └──────────────────┘              │
│                       │              │                           │
│                       │              ▼                           │
│                       │        LoadExternalComponent            │
│                       │              │                           │
│                       │              ▼                           │
│                       │        LangSmith Bundle Server           │
│                       │              │                           │
│                       │              ▼                           │
│                       │        agent/ui.tsx                     │
│                       │        (CardComponent)                  │
│                       │              │                           │
│                       │              ▼                           │
│                       │        Shadow DOM (isolated)             │
│                       │              │                           │
│                       └──────────────┘                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 1.9 ADDED Requirements (from C007 exploration)

### Requirement: Designer Agent State Awareness

Designer agent SHALL access `state.ui` to see existing widgets before emitting new ones.

#### Scenario: Avoid repeating widgets
- **WHEN** Designer node executes
- **THEN** agent reads `state.ui` to see existing widget names
- **AND** agent selects complementary widgets (not repeats)
- **AND** agent uses `push_ui_message()` to emit new widget
- **AND** UI state automatically updated via `ui_message_reducer`

### Requirement: Streaming with Merge

Backend nodes SHALL support streaming updates to same UI message using `merge=True`.

#### Scenario: Progressive content update
- **WHEN** node streams content (e.g., LLM generation)
- **THEN** initial `push_ui_message()` creates UI message
- **AND** subsequent calls use same `id` + `merge=True`
- **AND** props are merged (not replaced)
- **AND** component re-renders with merged props
- **AND** no duplicate UI messages created

---

**Next Artifact**: design.md
