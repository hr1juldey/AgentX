# Spec: pydantic-zod-sync

**File**: `specs/pydantic-zod-sync/spec.md`

## 1.1 Purpose

Define the synchronization mechanism between backend Pydantic v2 models and frontend Zod schemas, ensuring single source of truth and type safety across the stack.

## 1.2 Scope

**In Scope**:
- Pydantic v2 model definitions (backend)
- Zod schema definitions (frontend)
- Type mapping rules (Python → TypeScript)
- Field alias handling
- Validation parity

**Out of Scope**:
- UI descriptor contracts (see ui-descriptor-contracts spec)
- WebSocket protocol (see websocket-protocol spec)
- LangGraph server protocol (see C003-agent-pipeline)

## 1.3 Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-PZ-001 | Pydantic models SHALL use v2 syntax with `pydantic.BaseModel` | Must |
| FR-PZ-002 | Zod schemas SHALL match Pydantic models field-by-field | Must |
| FR-PZ-003 | Field names SHALL use alias mapping for snake_case → camelCase | Must |
| FR-PZ-004 | Optional fields SHALL be optional in both Pydantic and Zod | Must |
| FR-PZ-005 | Enum values SHALL match exactly (case-sensitive) | Must |
| FR-PZ-006 | Nested objects SHALL be recursively mapped | Must |
| FR-PZ-007 | Array types SHALL map `list[T]` → `z.array(TSchema)` | Must |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-PZ-001 | Type checking on both ends (tsc --noEmit, pyright) | Must |
| NFR-PZ-002 | Runtime validation (Pydantic, Zod) | Must |
| NFR-PZ-003 | Single source of truth (LLD locks definitions) | Must |
| NFR-PZ-004 | Automated sync verification (CI check) | Should |

## 1.4 Data Model

### Type Mapping Table

| Python Type | Pydantic Field | TypeScript Type | Zod Schema | Notes |
|-------------|---------------|-----------------|------------|-------|
| `str` | `Field()` | `string` | `z.string()` | Direct mapping |
| `int` | `Field()` | `number` | `z.number()` | JS has no int/float distinction |
| `float` | `Field()` | `number` | `z.number()` | - |
| `bool` | `Field()` | `boolean` | `z.boolean()` | - |
| `list[T]` | `Field(default_factory=list)` | `T[]` | `z.array(TSchema)` | Recursive for nested objects |
| `dict[str, T]` | `Field(default_factory=dict)` | `Record<string, T>` | `z.record(z.unknown())` | Use `z.record(TSchema)` for uniform types |
| `T \| None` | `Field(default=None)` | `T \| undefined` | `TSchema.optional()` | Optional fields |
| `Optional[T]` | `Field(default=None)` | `T \| null` | `TSchema.nullable()` | Explicit null handling |
| `datetime` | `Field()` | `string` (ISO 8601) | `z.string().datetime()` | Serialize as ISO string |
| `UUID` | `Field()` | `string` | `z.string().uuid()` | Serialize as string |
| `Enum` | `enum.Enum` | `enum` | `z.enum([...])` | Values must match exactly |

### Field Alias Mapping

**Backend (Pydantic v2)**:
```python
from pydantic import BaseModel, Field

class SearchRequest(BaseModel):
    query: str = Field(alias="q")  # Backend: query, Frontend: q
    max_hops: int = Field(default=3, alias="maxHops")
    device_context: str = Field(default="desktop", alias="deviceContext")

    class Config:
        populate_by_name = True  # Allow both alias and field name
```

**Frontend (Zod)**:
```typescript
import { z } from 'zod';

export const SearchRequestSchema = z.object({
  q: z.string(),  // Matches alias
  maxHops: z.number().default(3),  // camelCase
  deviceContext: z.string().default("desktop"),
});

export type SearchRequest = z.infer<typeof SearchRequestSchema>;
```

### Complex Nested Example

**Backend (Pydantic v2)**:
```python
from pydantic import BaseModel, Field
from typing import Any, Dict

class CardAction(BaseModel):
    label: str
    action: str
    variant: str = Field(default="outline")

class CardDescriptor(BaseModel):
    descriptor_id: str = Field(alias="id")
    descriptor_type: str = Field(alias="type")
    title: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    actions: list[CardAction] = Field(default_factory=list)

    class Config:
        populate_by_name = True
```

**Frontend (Zod)**:
```typescript
import { z } from 'zod';

export const CardActionSchema = z.object({
  label: z.string(),
  action: z.string(),
  variant: z.string().default("outline"),
});

export const CardDescriptorSchema = z.object({
  id: z.string(),
  type: z.string(),
  title: z.string(),
  content: z.string(),
  metadata: z.record(z.unknown()).default({}),
  actions: z.array(CardActionSchema).default([]),
});

export type CardDescriptor = z.infer<typeof CardDescriptorSchema>;
```

## 1.5 API Contract

### Sync Verification

**CI Check** (add to pipeline):
```bash
# Backend: Verify Pydantic models
python -m py_compile agentx/ui/descriptors/*.py

# Frontend: Verify Zod schemas
npx tsc --noEmit

# Manual: Compare enum values
python scripts/sync_enums.py  # Custom script to verify enum parity
```

**Verification Script** (scripts/sync_enums.py):
```python
#!/usr/bin/env python3
"""Verify Pydantic enums match Zod enums exactly."""

import re
from pathlib import Path

def extract_zod_enum_typescript(file_path: Path) -> set[str]:
    """Extract enum values from Zod schema."""
    content = file_path.read_text()
    match = re.search(r'z\.enum\(\[(.*?)\]\)', content, re.DOTALL)
    if match:
        values = match.group(1)
        return {v.strip().strip('"\'') for v in values.split(',')}
    return set()

def extract_pydantic_enum_python(file_path: Path) -> set[str]:
    """Extract enum values from Pydantic model."""
    content = file_path.read_text()
    # Find Enum class and extract values
    match = re.search(r'class (\w+)\(str, Enum\):.*?"""(.*?)"""(.*?)(?=\nclass|\Z)', content, re.DOTALL)
    if match:
        values = re.findall(r'(\w+)\s*=\s*["\']([^"\']+)["\']', content)
        return {value for _, value in values}
    return set()

def main():
    backend_dir = Path("agentx/ui/descriptors")
    frontend_dir = Path("frontend/types")

    # Compare WidgetType enums
    backend_enum = extract_pydantic_enum_python(backend_dir / "base.py")
    frontend_enum = extract_zod_enum_typescript(frontend_dir / "descriptors.ts")

    if backend_enum != frontend_enum:
        print(f"ERROR: Enum mismatch!")
        print(f"  Backend: {backend_enum}")
        print(f"  Frontend: {frontend_enum}")
        return 1

    print("✓ All enums synchronized")
    return 0

if __name__ == "__main__":
    exit(main())
```

## 1.6 Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-PZ-001 | Field names use camelCase on frontend | Code review, linter |
| BR-PZ-002 | Field names use snake_case on backend | Code review, ruff |
| BR-PZ-003 | Aliases map backend → frontend names | Pydantic Field(alias=...) |
| BR-PZ-004 | Enum values match exactly (case-sensitive) | CI verification script |
| BR-PZ-005 | Optional fields use `.optional()` in Zod | Code review |
| BR-PZ-006 | Nested objects use recursive mapping | Code review |

## 1.7 Acceptance Criteria

- [ ] All Pydantic models have corresponding Zod schemas
- [ ] Field aliases map snake_case → camelCase
- [ ] Enum values match exactly
- [ ] Optional fields consistent across both
- [ ] Nested objects recursively mapped
- [ ] CI verification script passes
- [ ] Type checking passes (tsc --noEmit, pyright)

## 1.8 Type Sync Checklist

For each Pydantic model, verify:

| Check | Description | Status |
|-------|-------------|--------|
| Field names | camelCase in Zod, snake_case in Pydantic | ☐ |
| Field aliases | `Field(alias=...)` in Pydantic | ☐ |
| Optional fields | `.optional()` in Zod, `default=None` in Pydantic | ☐ |
| Enum values | Exact match (case-sensitive) | ☐ |
| Array types | `z.array(...)` for `list[...]` | ☐ |
| Dict types | `z.record(...)` for `dict[str, ...]` | ☐ |
| Nested objects | Recursive schema definitions | ☐ |

---

**Next Artifact**: design.md
