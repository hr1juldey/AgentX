# Spec: duration-memory

**File**: `specs/duration-memory/spec.md`

## 1.1 Purpose

Define duration-aware memory for tracking long-term states (e.g., "watched movie for 2 hours") with start/end timestamps and consolidation.

## 1.2 Scope

**In Scope**:
- State tracking (start/end times)
- Duration calculation
- Active states query
- Consolidation of duration events
- LangGraph server-driven UI for active states display

**Out of Scope**:
- Point events (handled by temporal-rag)
- State visualization UI design (see C008-organic-ui)

## 1.3 Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-DM-001 | Service MUST track state start time | Must |
| FR-DM-002 | Service MUST calculate duration on state end | Must |
| FR-DM-003 | Service MUST store duration as consolidated memory | Must |
| FR-DM-004 | Service MUST support multiple concurrent states per user | Must |
| FR-DM-005 | Service MUST auto-end stale states after 24 hours | Should |
| FR-DM-006 | Service MUST emit active state UI updates | Must |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-DM-001 | Duration calculation MUST be accurate to within 1 second | Must |
| NFR-DM-002 | Active states query MUST complete within 100ms | Must |

## 1.4 Data Model

```python
# Locked from research:07_temporal_rag.md:271-354
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID, uuid4

@dataclass
class DurationState:
    """Active state tracking."""
    state_id: UUID
    state_type: str  # e.g., "watching_movie", "exercising"
    user_id: UUID
    start_time: datetime
    attributes: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary for UI display."""
        return {
            "stateId": str(self.state_id),
            "stateType": self.state_type,
            "userId": str(self.user_id),
            "startTime": self.start_time.isoformat(),
            "attributes": self.attributes,
        }

@dataclass
class DurationMemory:
    """Track states with durations."""
    active_states: Dict[str, Dict] = field(default_factory=dict)

    def start_state(self, state_id: str, state_type: str, attributes: Dict, user_id: str) -> UUID:
        """Start tracking a state."""
        state_uuid = uuid4()
        state = DurationState(
            state_id=state_uuid,
            state_type=state_type,
            user_id=UUID(user_id),
            start_time=datetime.utcnow(),
            attributes=attributes
        )
        self.active_states[str(state_uuid)] = state.to_dict()
        return state_uuid

    def end_state(self, state_id: str) -> Optional[Dict]:
        """End tracking a state and return duration info."""
        state_data = self.active_states.pop(state_id, None)
        if not state_data:
            return None

        start_time = datetime.fromisoformat(state_data["startTime"])
        end_time = datetime.utcnow()
        duration_seconds = int((end_time - start_time).total_seconds())

        return {
            "stateId": state_id,
            "stateType": state_data["stateType"],
            "duration": duration_seconds,
            "startTime": state_data["startTime"],
            "endTime": end_time.isoformat(),
        }

    def get_active_states(self, user_id: str) -> List[Dict]:
        """Get all active states for a user."""
        return [
            state for state in self.active_states.values()
            if state["userId"] == user_id
        ]
```

## 1.5 API Contract

### REST Endpoints

| Method | Path | Request | Response | Status Codes |
|--------|------|---------|----------|--------------|
| POST | `/api/v1/memory/start-state` | `StartStateCommand` | `StartStateResponse` | 201, 400, 500 |
| POST | `/api/v1/memory/end-state/{state_id}` | - | `EndStateResponse` | 200, 404, 500 |
| GET | `/api/v1/memory/active-states/{user_id}` | - | `ActiveStatesResponse` | 200, 404, 500 |

### Backend DTOs (Pydantic v2)

```python
from pydantic import BaseModel, Field
from uuid import UUID

class StartStateCommand(BaseModel):
    state_type: str = Field(alias="stateType")
    user_id: UUID = Field(alias="userId")
    attributes: Dict[str, str] = Field(default_factory=dict)

class StartStateResponse(BaseModel):
    state_id: UUID = Field(alias="stateId")
    start_time: datetime = Field(alias="startTime")
    message: str

class EndStateResponse(BaseModel):
    state_id: UUID = Field(alias="stateId")
    state_type: str = Field(alias="stateType")
    duration_seconds: int = Field(alias="durationSeconds")
    duration_formatted: str = Field(alias="durationFormatted")
    message: str

class ActiveStateDTO(BaseModel):
    state_id: UUID = Field(alias="stateId")
    state_type: str = Field(alias="stateType")
    start_time: datetime = Field(alias="startTime")
    attributes: Dict[str, str] = Field(default_factory=dict)

class ActiveStatesResponse(BaseModel):
    user_id: UUID = Field(alias="userId")
    active_states: List[ActiveStateDTO] = Field(alias="activeStates")
    count: int
```

### Frontend Zod Schemas

```typescript
import { z } from 'zod';

export const StartStateCommandSchema = z.object({
  stateType: z.string().min(1),
  userId: z.string().uuid(),
  attributes: z.record(z.string()).default({}),
});

export const ActiveStateDTOSchema = z.object({
  stateId: z.string().uuid(),
  stateType: z.string(),
  startTime: z.string().datetime(),
  attributes: z.record(z.string()).default({}),
});

export const ActiveStatesResponseSchema = z.object({
  userId: z.string().uuid(),
  activeStates: z.array(ActiveStateDTOSchema),
  count: z.number().int().min(0),
});
```

## 1.6 Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-DM-001 | Duration = end_time - start_time (seconds) | DurationMemory.end_state() |
| BR-DM-002 | Stale states auto-end after 24 hours | DurationMemory._cleanup_stale_states() |
| BR-DM-003 | Consolidated duration memory includes "Duration: X for Ys" | DurationMemory._create_consolidated_memory() |
| BR-DM-004 | Active state changes emit UI updates | push_ui_message() calls |

## 1.7 Acceptance Criteria

- [ ] States tracked with start_time
- [ ] Duration calculated correctly (end - start)
- [ ] Duration memory stored to Tier 3 on consolidation
- [ ] Active states queryable by user_id
- [ ] Multiple concurrent states supported
- [ ] Stale states auto-end after 24 hours
- [ ] Duration calculation accurate within 1 second
- [ ] Active states query within 100ms
- [ ] Active states displayed via server-driven UI widgets
- [ ] State duration formatted human-readable (e.g., "2h 30m")

## 1.8 Frontend UI Integration (from C007 Frontend Architecture)

### Active States UI Updates

Duration memory service MUST emit UI messages for state changes:

```python
from langgraph.graph.ui import push_ui_message

# Emit when state starts
push_ui_message(
    "hopProgress",
    {
        "label": state_type,
        "status": "active",
        "startedAt": datetime.utcnow().isoformat(),
        "metadata": {"stateId": str(state_id)},
    },
    message=None
)

# Emit when state ends (update same message with merge=True)
push_ui_message(
    "hopProgress",
    {
        "label": state_type,
        "status": "completed",
        "duration": duration_seconds,
        "durationFormatted": format_duration(duration_seconds),
    },
    message=None,
    id=state_message_id,
    merge=True
)
```

### Active States Widget

```typescript
// src/agent/ui.tsx (colocated with graph.py)
import { HopProgressComponent } from "./widgets/HopProgressWidget";

export default {
  hopProgress: HopProgressComponent,
};
```

```typescript
// src/agent/widgets/HopProgressWidget.tsx
interface HopProgressProps {
  label: string;
  status: "active" | "completed";
  startedAt?: string;
  duration?: number;
  durationFormatted?: string;
}

export function HopProgressComponent(props: HopProgressProps) {
  const isActive = props.status === "active";

  return (
    <div className={`hop-progress ${isActive ? "active" : "completed"}`}>
      <div className="hop-icon">
        {isActive ? <Spinner /> : <CheckCircle />}
      </div>
      <div className="hop-details">
        <span className="label">{props.label}</span>
        {isActive ? (
          <span className="status">In progress...</span>
        ) : (
          <span className="duration">{props.durationFormatted}</span>
        )}
      </div>
    </div>
  );
}
```

### Frontend Integration Pattern

```tsx
// File: frontend/app/memory/page.tsx
import { useStream } from "@langchain/langgraph-sdk/react";
import { LoadExternalComponent } from "@langchain/langgraph-sdk/react-ui";

function ActiveStatesPage() {
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

  return (
    <div>
      <h2>Active States</h2>
      {/* Hop progress widgets from server */}
      {values.ui?.filter(u => u.name === "hopProgress").map((ui) => (
        <LoadExternalComponent
          key={ui.id}
          stream={thread}
          message={ui}
          fallback={<SkeletonHopProgress />}
        />
      ))}
    </div>
  );
}
```

---

**Related Specs**:
- `specs/memory-consolidation/spec.md` - Consolidation of duration events
- `specs/temporal-rag/spec.md` - Temporal metadata
- C002 data contracts - Pydantic ↔ Zod mappings
