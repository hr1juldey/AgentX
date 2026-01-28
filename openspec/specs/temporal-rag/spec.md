# Spec: temporal-rag

**File**: `specs/temporal-rag/spec.md`

## 1.1 Purpose

Define time-aware retrieval-augmented generation with temporal filtering, fact invalidation, and multi-hop search across Tier 2 and Tier 3 memories.

## 1.2 Scope

**In Scope**:
- Temporal metadata enrichment (created_at, valid_from, valid_until)
- Temporal classification (preference, state, event, plan, fact)
- Time-filtered search (recent, historical, all)
- Fact invalidation during retrieval
- Multi-hop retrieval (Tier 2 + Tier 3)
- LangGraph server-driven UI for search results

**Out of Scope**:
- Memory storage (covered by consolidation spec)
- Memory visualization UI design (see C008-organic-ui)

## 1.3 Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-TR-001 | Service MUST add temporal metadata to all memories | Must |
| FR-TR-002 | Service MUST classify memory by temporal_type (preference, state, event, plan, fact) | Must |
| FR-TR-003 | Service MUST support time-filtered search (recent, historical, all) | Must |
| FR-TR-004 | Service MUST invalidate outdated facts during retrieval | Must |
| FR-TR-005 | Service MUST search both Tier 2 and Tier 3 (multi-hop) | Must |
| FR-TR-006 | Service MUST weight recent memories higher than historical | Should |
| FR-TR-007 | Service MUST emit search results via `push_ui_message()` | Must |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-TR-001 | Temporal classification accuracy MUST be >90% | Must |
| NFR-TR-002 | Time-filtered search MUST complete within 500ms | Must |
| NFR-TR-003 | Multi-hop retrieval MUST be +15% better than Tier 3 alone | Should |

## 1.4 Data Model

```python
# Temporal metadata (added to all memories)
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from enum import Enum

class TemporalType(str, Enum):
    PREFERENCE = "preference"
    STATE = "state"
    EVENT = "event"
    PLAN = "plan"
    FACT = "fact"

@dataclass
class TemporalMetadata:
    """Temporal metadata for time-aware RAG."""
    created_at: datetime
    modified_at: datetime
    valid_from: datetime
    valid_until: Optional[datetime]  # None means still valid
    temporal_type: TemporalType
    supersedes: List[UUID]  # Memory IDs this one invalidates
    superseded_by: Optional[UUID]  # If this memory is outdated
```

## 1.5 API Contract

### REST Endpoints

| Method | Path | Request | Response | Status Codes |
|--------|------|---------|----------|--------------|
| POST | `/api/v1/memory/search` | `SearchMemoryCommand` | `SearchMemoryResponse` | 200, 400, 500 |
| POST | `/api/v1/memory/store` | `StoreMemoryCommand` | `StoreMemoryResponse` | 201, 400, 500 |

### Backend DTOs (Pydantic v2)

```python
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Literal

class SearchMemoryCommand(BaseModel):
    query: str
    user_id: UUID = Field(alias="userId")
    time_filter: Literal["recent", "historical", "all"] = Field(default="all", alias="timeFilter")
    max_results: int = Field(default=10, alias="maxResults")
    temporal_types: Optional[List[TemporalType]] = Field(default=None, alias="temporalTypes")

class SearchResult(BaseModel):
    memory_id: UUID = Field(alias="memoryId")
    content: str
    temporal_type: TemporalType = Field(alias="temporalType")
    created_at: datetime = Field(alias="createdAt")
    valid_until: Optional[datetime] = Field(alias="validUntil")
    score: float
    superseded: bool = False  # True if this memory is outdated

class SearchMemoryResponse(BaseModel):
    results: List[SearchResult]
    total_found: int = Field(alias="totalFound")
    query_time_ms: int = Field(alias="queryTimeMs")

class StoreMemoryCommand(BaseModel):
    content: str
    user_id: UUID = Field(alias="userId")
    temporal_type: TemporalType = Field(default=TemporalType.FACT, alias="temporalType")
    metadata: Optional[Dict[str, Any]] = None

class StoreMemoryResponse(BaseModel):
    memory_id: UUID = Field(alias="memoryId")
    created_at: datetime = Field(alias="createdAt")
    message: str
```

### Frontend Zod Schemas

```typescript
import { z } from 'zod';

export const TemporalTypeSchema = z.enum([
  "preference",
  "state",
  "event",
  "plan",
  "fact",
]);

export const SearchMemoryCommandSchema = z.object({
  query: z.string().min(1),
  userId: z.string().uuid(),
  timeFilter: z.enum(["recent", "historical", "all"]).default("all"),
  maxResults: z.number().int().min(1).max(100).default(10),
  temporalTypes: z.array(TemporalTypeSchema).optional(),
});

export const SearchResultSchema = z.object({
  memoryId: z.string().uuid(),
  content: z.string(),
  temporalType: TemporalTypeSchema,
  createdAt: z.string().datetime(),
  validUntil: z.string().datetime().optional(),
  score: z.number().min(0).max(1),
  superseded: z.boolean().default(false),
});

export const SearchMemoryResponseSchema = z.object({
  results: z.array(SearchResultSchema),
  totalFound: z.number().int().min(0),
  queryTimeMs: z.number().int().min(0),
});

export const StoreMemoryCommandSchema = z.object({
  content: z.string().min(1),
  userId: z.string().uuid(),
  temporalType: TemporalTypeSchema.default("fact"),
  metadata: z.record(z.unknown()).optional(),
});
```

## 1.6 Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-TR-001 | All memories MUST have temporal metadata | MemoryRepository.store_memory() |
| BR-TR-002 | Recent search = last 30 days | TemporalRAGService._build_time_filter() |
| BR-TR-003 | Historical search = older than 30 days | TemporalRAGService._build_time_filter() |
| BR-TR-004 | Outdated facts filtered at retrieval | TemporalRAGService._invalidate_outdated_facts() |
| BR-TR-005 | Preferences weighted 2x higher than facts | TemporalRAGService._weight_results() |
| BR-TR-006 | Search results emitted via UI messages | push_ui_message() calls |

## 1.7 Acceptance Criteria

- [ ] All memories have temporal metadata
- [ ] Temporal classification accuracy >90%
- [ ] Time-filtered search returns correct time windows
- [ ] Outdated facts filtered or marked with superseded_by
- [ ] Multi-hop search merges Tier 2 and Tier 3 results
- [ ] Time-filtered search completes within 500ms
- [ ] Multi-hop retrieval +15% better than Tier 3 alone
- [ ] Search results displayed via server-driven UI widgets
- [ ] Superseded memories visually distinguished

## 1.8 Frontend UI Integration (from C007 Frontend Architecture)

### Search Results UI Updates

Temporal RAG service MUST emit UI messages for search results:

```python
from langgraph.graph.ui import push_ui_message

# Emit search results as cards
for idx, result in enumerate(search_results):
    push_ui_message(
        "searchResult",
        {
            "title": f"Memory {idx + 1}",
            "content": result.content,
            "metadata": {
                "temporalType": result.temporal_type.value,
                "createdAt": result.created_at.isoformat(),
                "score": result.score,
                "superseded": result.superseded,
            },
        },
        message=message
    )

# Emit summary card
push_ui_message(
    "card",
    {
        "title": "Search Complete",
        "content": f"Found {total_found} memories in {query_time_ms}ms",
        "metadata": {"variant": "info"},
    },
    message=message
)
```

### Search Result Widget

```typescript
// src/agent/ui.tsx (colocated with graph.py)
import { SearchResultComponent } from "./widgets/SearchResultWidget";

export default {
  searchResult: SearchResultComponent,
  card: CardComponent,
};
```

```typescript
// src/agent/widgets/SearchResultWidget.tsx
interface SearchResultProps {
  title: string;
  content: string;
  metadata: {
    temporalType: string;
    createdAt: string;
    score: number;
    superseded: boolean;
  };
}

export function SearchResultComponent(props: SearchResultProps) {
  const isSuperseded = props.metadata.superseded;

  return (
    <div className={`search-result ${isSuperseded ? "superseded" : ""}`}>
      <h4>{props.title}</h4>
      <p>{props.content}</p>
      <div className="metadata">
        <span className="type">{props.metadata.temporalType}</span>
        <span className="score">Score: {Math.round(props.metadata.score * 100)}%</span>
        {isSuperseded && <span className="outdated">Outdated</span>}
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

function MemorySearchPage() {
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
      {/* Search result widgets from server */}
      {values.ui?.filter(u => u.name === "searchResult").map((ui) => (
        <LoadExternalComponent
          key={ui.id}
          stream={thread}
          message={ui}
          fallback={<SkeletonSearchResult />}
        />
      ))}
    </div>
  );
}
```

---

**Related Specs**:
- `specs/memory-consolidation/spec.md` - Consolidation of memories
- `specs/duration-memory/spec.md` - Duration event handling
- C002 data contracts - Pydantic ↔ Zod mappings
- C003 agent pipeline - LangGraph integration for RAG context
