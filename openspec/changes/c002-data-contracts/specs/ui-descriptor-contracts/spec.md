# Spec: ui-descriptor-contracts

**File**: `specs/ui-descriptor-contracts/spec.md`

## 1.1 Purpose

Define the UI descriptor contracts between backend (LangGraph) and frontend (Next.js), including Pydantic v2 models for backend and Zod schemas for frontend with Shadow DOM isolation.

## 1.2 Scope

**In Scope**:
- UIDescriptor base class with LangGraph AnyUIMessage mapping
- 12 widget types from R014 + C007 exploration
- Pydantic v2 backend models
- Zod frontend validation schemas
- Shadow DOM props interface
- Component registration mapping

**Out of Scope**:
- WebSocket protocol (see websocket-protocol spec)
- LangGraph StateGraph definition (see C003-agent-pipeline)
- Organic UI visual implementation (see C008-organic-ui)

## 1.3 Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-UI-DESC-001 | Backend SHALL use Pydantic v2 for all descriptor models | Must |
| FR-UI-DESC-002 | Frontend SHALL use Zod for all descriptor validation | Must |
| FR-UI-DESC-003 | Pydantic models SHALL map to LangGraph AnyUIMessage format | Must |
| FR-UI-DESC-004 | Frontend Zod schemas SHALL match backend Pydantic exactly | Must |
| FR-UI-DESC-005 | Components SHALL use Shadow DOM for style isolation | Must |
| FR-UI-DESC-006 | Component props SHALL be type-safe between backend and frontend | Must |
| FR-UI-DESC-007 | Widget types SHALL include all 12 types from R014 + C007 | Must |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-UI-DESC-001 | Type safety enforced at build time (tsc --noEmit) | Must |
| NFR-UI-DESC-002 | Runtime validation with Zod on frontend | Must |
| NFR-UI-DESC-003 | Pydantic runtime validation on backend | Must |
| NFR-UI-DESC-004 | Shadow DOM guarantees no style conflicts | Must |

## 1.4 Data Model

### Backend (Pydantic v2)

```python
# Locked from C007 extract.md + domain_model.md
from pydantic import BaseModel, Field
from typing import Any, Dict, Optional
from enum import Enum

class WidgetType(str, Enum):
    """12 widget types from R014 + C007 exploration."""
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

class UIDescriptor(BaseModel):
    """Base UI descriptor that maps to LangGraph AnyUIMessage."""
    descriptor_id: str = Field(alias="id")
    descriptor_type: WidgetType = Field(alias="type")
    title: Optional[str] = None
    content: Optional[str | dict[str, Any]] = None
    metadata: Dict[str, Any] = {}
    timestamp: str

    class Config:
        populate_by_name = True  # Allow alias usage
```

### Frontend (Zod)

```typescript
import { z } from 'zod';

// Must match backend WidgetType exactly
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

// Must match backend UIDescriptor exactly
export const UIDescriptorSchema = z.object({
  id: z.string(),
  type: WidgetTypeSchema,
  title: z.string().optional(),
  content: z.union([z.string(), z.record(z.unknown())]).optional(),
  metadata: z.record(z.unknown()).optional(),
});

export type UIDescriptor = z.infer<typeof UIDescriptorSchema>;
```

### LangGraph AnyUIMessage Mapping

```python
# Backend: push_ui_message maps UIDescriptor to AnyUIMessage
from langgraph.graph.ui import push_ui_message

async def designer_node(state: AgentState):
    descriptor = UIDescriptor(
        id=str(uuid.uuid4()),
        descriptor_type=WidgetType.CARD,
        title="Search Results",
        content={"results": [...]},
        metadata={"count": 5}
    )

    # Maps to AnyUIMessage format
    push_ui_message(
        "card",  # Component name (matches type)
        {
            "title": descriptor.title,
            "content": descriptor.content,
        },
        message=message
    )
```

## 1.5 API Contract

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

### Component Export Pattern (ui.tsx)

```typescript
// Backend: agent/ui.tsx (colocated with graph)
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

### Shadow DOM Props Interface

```typescript
// Each component receives props matching backend schema
interface CardProps {
  title: string;
  content: string;
  metadata?: {
    icon?: string;
    actions?: Array<{label: string; action: string}>;
  };
}

// Component uses Shadow DOM for style isolation
export function CardComponent(props: CardProps) {
  return (
    <div className="widget-card">
      <h3>{props.title}</h3>
      <p>{props.content}</p>
    </div>
  );
}
```

## 1.6 Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-UI-DESC-001 | WidgetType enum must match exactly | Build check, compare enum values |
| BR-UI-DESC-002 | Pydantic alias names map to frontend names | Pydantic Config(populate_by_name=True) |
| BR-UI-DESC-003 | All components use Shadow DOM | Code review, LoadExternalComponent wrapper |
| BR-UI-DESC-004 | Props are type-safe | TypeScript strict mode, tsc --noEmit |
| BR-UI-DESC-005 | Zod schemas validate at runtime | Frontend middleware |

## 1.7 Acceptance Criteria

- [ ] All 12 widget types defined in both backend and frontend
- [ ] Pydantic models use v2 syntax with Field aliases
- [ ] Zod schemas match Pydantic models exactly
- [ ] Components use Shadow DOM for style isolation
- [ ] Type safety enforced (no `any` types in props)
- [ ] Runtime validation with Zod on frontend
- [ ] Component registration in langgraph.json
- [ ] UI state tracked via ui_message_reducer (see C003)

## 1.8 ADDED Requirements (from C007 exploration)

### Requirement: LangGraph Server-Driven UI Mapping

UI descriptors SHALL map to LangGraph AnyUIMessage format for server-driven UI.

#### Scenario: Backend emits UI
- **WHEN** node calls `push_ui_message(component_name, props)`
- **THEN** props match component's TypeScript interface
- **AND** component_name exists in ui.tsx export
- **AND** LangSmith bundles and serves component
- **AND** frontend fetches via LoadExternalComponent

#### Scenario: Frontend renders component
- **WHEN** LoadExternalComponent receives AnyUIMessage
- **THEN** component is fetched from LangSmith bundle server
- **THEN** props are validated against Zod schema
- **AND** Shadow DOM prevents style conflicts
- **AND** component re-renders on props update

### Requirement: Shadow DOM Style Isolation

All server-driven UI components SHALL use Shadow DOM for style isolation.

#### Scenario: Style isolation
- **WHEN** component is rendered via LoadExternalComponent
- **THEN** component styles are scoped to Shadow DOM
- **AND** global styles don't affect component
- **AND** component styles don't leak to other components
- **AND** design tokens (from C008) are passed as props

---

**Next Artifact**: design.md
