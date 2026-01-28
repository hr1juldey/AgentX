# Spec: memory-consolidation

**File**: `specs/memory-consolidation/spec.md`

## 1.1 Purpose

Define memory consolidation service that moves memories from Tier 2 (session-scoped Qdrant) to Tier 3 (persistent Qdrant + Mem0AI) with merging, invalidation, and summarization.

## 1.2 Scope

**In Scope**:
- Tier 2 → Tier 3 consolidation on trigger
- Duplicate memory merging (same entity/topic)
- Fact invalidation (new supersedes old)
- Duration event summarization
- Three trigger types: SCHEDULED, MANUAL, PRE_QUERY
- LangGraph server-driven UI integration for consolidation status

**Out of Scope**:
- Real-time memory updates (handled by C003)
- Memory visualization UI design (see C008-organic-ui)

## 1.3 Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-MC-001 | Service MUST consolidate Tier 2 memories to Tier 3 on trigger | Must |
| FR-MC-002 | Service MUST merge duplicate memories (same entity/topic) | Must |
| FR-MC-003 | Service MUST invalidate outdated facts (new supersedes old) | Must |
| FR-MC-004 | Service MUST summarize duration events into single memories | Must |
| FR-MC-005 | Service MUST support three triggers: SCHEDULED (every 10), MANUAL, PRE_QUERY | Must |
| FR-MC-006 | Service MUST track consolidation status (PENDING → IN_PROGRESS → COMPLETED) | Must |
| FR-MC-007 | Service MUST emit UI updates via `push_ui_message()` during consolidation | Must |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-MC-001 | Consolidation MUST complete within 30 seconds | Must |
| NFR-MC-002 | Merge rate MUST be >10% (memories_merged / memories_processed) | Should |
| NFR-MC-003 | MemoryRepository MUST be thread-safe for concurrent access | Must |
| NFR-MC-004 | UI updates MUST be emitted for status changes | Should |

## 1.4 Data Model

```python
# Locked from LLD: domain_model.md:189-269
from dataclasses import dataclass
from uuid import UUID
from datetime import datetime
from typing import Optional
from enum import Enum

class ConsolidationTrigger(str, Enum):
    SCHEDULED = "scheduled"  # Every 10 interactions
    MANUAL = "manual"  # User requested
    PRE_QUERY = "pre_query"  # Before query processing

class ConsolidationStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class MemoryConsolidationEntity:
    """Represents a memory consolidation operation.

    Consolidation moves memories from Tier 2 (Agent's Qdrant) to Tier 3 (User's Qdrant + Mem0AI).
    """
    consolidation_id: UUID
    session_id: UUID
    trigger: ConsolidationTrigger
    status: ConsolidationStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    memories_processed: int = 0
    memories_merged: int = 0
    memories_invalidated: int = 0
    error_message: Optional[str] = None

    def start(self) -> None:
        """Transition to IN_PROGRESS status."""
        self.status = ConsolidationStatus.IN_PROGRESS
        self.started_at = datetime.utcnow()

    def complete(self, processed: int, merged: int, invalidated: int) -> None:
        """Mark consolidation as COMPLETED."""
        self.status = ConsolidationStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.memories_processed = processed
        self.memories_merged = merged
        self.memories_invalidated = invalidated

    def fail(self, error: str) -> None:
        """Mark consolidation as FAILED."""
        self.status = ConsolidationStatus.FAILED
        self.completed_at = datetime.utcnow()
        self.error_message = error

    def duration_seconds(self) -> Optional[int]:
        """Calculate consolidation duration in seconds."""
        if self.started_at and self.completed_at:
            return int((self.completed_at - self.started_at).total_seconds())
        return None

    def merge_rate(self) -> float:
        """Calculate merge rate (merged / processed)."""
        if self.memories_processed > 0:
            return self.memories_merged / self.memories_processed
        return 0.0
```

## 1.5 API Contract

### REST Endpoints

| Method | Path | Request | Response | Status Codes |
|--------|------|---------|----------|--------------|
| POST | `/api/v1/memory/consolidate` | `ConsolidateMemoryCommand` | `ConsolidateMemoryResponse` | 201, 400, 500 |
| GET | `/api/v1/memory/consolidations/{consolidation_id}` | - | `ConsolidationStatusResponse` | 200, 404, 500 |

### Backend DTOs (Pydantic v2)

```python
from pydantic import BaseModel, Field

class ConsolidateMemoryCommand(BaseModel):
    session_id: UUID = Field(alias="sessionId")
    trigger: ConsolidationTrigger = Field(default=ConsolidationTrigger.MANUAL)

class ConsolidateMemoryResponse(BaseModel):
    consolidation_id: UUID = Field(alias="consolidationId")
    status: ConsolidationStatus
    message: str

class ConsolidationStatusResponse(BaseModel):
    consolidation_id: UUID = Field(alias="consolidationId")
    status: ConsolidationStatus
    memories_processed: int = Field(alias="memoriesProcessed")
    memories_merged: int = Field(alias="memoriesMerged")
    memories_invalidated: int = Field(alias="memoriesInvalidated")
    created_at: datetime = Field(alias="createdAt")
    completed_at: Optional[datetime] = Field(alias="completedAt")
    error_message: Optional[str] = Field(alias="errorMessage")
```

### Frontend Zod Schemas

```typescript
import { z } from 'zod';

export const ConsolidationTriggerSchema = z.enum([
  "scheduled",
  "manual",
  "pre_query",
]);

export const ConsolidationStatusSchema = z.enum([
  "pending",
  "in_progress",
  "completed",
  "failed",
]);

export const ConsolidateMemoryCommandSchema = z.object({
  sessionId: z.string().uuid(),
  trigger: ConsolidationTriggerSchema.default("manual"),
});

export const ConsolidationStatusResponseSchema = z.object({
  consolidationId: z.string().uuid(),
  status: ConsolidationStatusSchema,
  memoriesProcessed: z.number().int().min(0),
  memoriesMerged: z.number().int().min(0),
  memoriesInvalidated: z.number().int().min(0),
  createdAt: z.string().datetime(),
  completedAt: z.string().datetime().optional(),
  errorMessage: z.string().optional(),
});
```

## 1.6 Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-MC-001 | SCHEDULED trigger fires every 10 interactions | ConsolidationService counter |
| BR-MC-002 | Fact invalidation marks old with superseded_by | ConsolidateMemoryUseCase |
| BR-MC-003 | Duration events summarized as single memory | DurationMemoryService |
| BR-MC-004 | Failed consolidation MUST preserve error message | MemoryConsolidationEntity.fail() |
| BR-MC-005 | UI updates emitted on each status transition | push_ui_message() calls |

## 1.7 Acceptance Criteria

- [ ] Consolidation reduces Tier 2 memory count
- [ ] Duplicate memories merged (merge_rate > 0.1)
- [ ] Outdated facts marked with superseded_by
- [ ] Duration events summarized as single memories
- [ ] Consolidation status transitions PENDING → IN_PROGRESS → COMPLETED
- [ ] All three triggers work (SCHEDULED, MANUAL, PRE_QUERY)
- [ ] Consolidation completes within 30 seconds
- [ ] LLD alignment verified (100% field match)
- [ ] UI updates emitted for status changes via `push_ui_message()`
- [ ] Progress widget displays consolidation progress

## 1.8 Frontend UI Integration (from C007 Frontend Architecture)

### Consolidation Status UI Updates

Consolidation service MUST emit UI messages for status changes:

```python
from langgraph.graph.ui import push_ui_message

# Emit when consolidation starts
push_ui_message(
    "progress",
    {
        "title": "Consolidating Memories",
        "status": "in_progress",
        "current": 0,
        "total": memories_count,
        "message": f"Processing {memories_count} memories...",
    },
    message=None
)

# Emit progress updates
push_ui_message(
    "progress",
    {
        "title": "Consolidating Memories",
        "status": "in_progress",
        "current": processed,
        "total": total,
        "message": f"Merged {merged} duplicates, invalidated {invalidated} outdated facts...",
    },
    message=None,
    id=progress_id,
    merge=True
)

# Emit when consolidation completes
push_ui_message(
    "card",
    {
        "title": "Consolidation Complete",
        "content": f"Processed {processed} memories, merged {merged} duplicates, invalidated {invalidated} facts.",
        "metadata": {"variant": "success"},
    },
    message=None
)
```

### Consolidation Progress Widget

```typescript
// src/agent/ui.tsx (colocated with graph.py)
export default {
  progress: ProgressComponent,
  card: CardComponent,
};
```

```typescript
// src/agent/widgets/ProgressComponent.tsx
interface ProgressProps {
  title: string;
  status: "pending" | "in_progress" | "completed" | "failed";
  current: number;
  total: number;
  message: string;
}

export function ProgressComponent(props: ProgressProps) {
  const percent = Math.round((props.current / props.total) * 100);

  return (
    <div className="consolidation-progress">
      <h3>{props.title}</h3>
      <div className="progress-bar">
        <div className="progress-fill" style={{ width: `${percent}%` }} />
      </div>
      <p>{props.message}</p>
      <span>{props.current} / {props.total} ({percent}%)</span>
    </div>
  );
}
```

### Frontend Integration Pattern

```tsx
// File: frontend/app/memory/page.tsx
import { useStream } from "@langchain/langgraph-sdk/react";
import { LoadExternalComponent } from "@langchain/langgraph-sdk/react-ui";

function MemoryPage() {
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
      {/* Progress widget from server */}
      {values.ui?.filter(u => u.name === "progress").map((ui) => (
        <LoadExternalComponent
          key={ui.id}
          stream={thread}
          message={ui}
          fallback={<SkeletonProgress />}
        />
      ))}
    </div>
  );
}
```

---

**Related Specs**:
- `specs/temporal-rag/spec.md` - Temporal metadata for RAG
- `specs/duration-memory/spec.md` - Duration event handling
- C002 data contracts - Pydantic ↔ Zod mappings
- C003 agent pipeline - LangGraph server-driven UI integration
