# Function Postmortem: domain/entities/ui_descriptor.py

## Metadata
- **File**: domain/entities/ui_descriptor.py
- **Lines of Code**: 53
- **Purpose**: Core domain entity for UI widgets
- **Dependencies**: `typing`, `pydantic`

---

## Analysis

**File Status**: CANONICAL DOMAIN ENTITY

**Purpose**: Represents a UI widget in the domain layer, independent of API concerns. This is the core entity that exists at the heart of the system.

---

## Classes Extracted

### UIDescriptor

**Purpose**: UI descriptor domain entity

**Signature**:
```python
class UIDescriptor(BaseModel):
```

**Lines**: 12-52

**Fields**:
```python
class UIDescriptor(BaseModel):
    """UI descriptor domain entity.

    Represents a UI widget in the domain layer, independent of API concerns.
    This is the core entity that exists at the heart of the system.

    Widget types include multi-hop search widgets:
    - search-result: Final answer with citations
    - hop-progress: Real-time hop progress with expandable details
    - citation-card: Expandable citation cards
    """

    id: str
    type: Literal[
        "markdown",
        "card",
        "form",
        "progress",
        "action",
        "confirmation",
        "voice",
        "image",
        "gallery",
        "chart",
        "search-result",
        "hop-progress",
        "citation-card",
    ]
    timestamp: str
    dismissible: bool = True
    content: str | None = None
    title: str | None = None
    metadata: dict[str, Any] = {}
    # Multi-hop search optional fields
    progress: float | None = None
    hops_completed: int | None = None
    total_hops: int | None = None
    reflection_reasoning: str | None = None
    citations: list[dict[str, Any]] | None = None
    hop_events: list[dict[str, Any]] | None = None
    eta_seconds: float | None = None
```

**What Works**:
- ✅ Canonical domain entity location
- ✅ Literal type constraint (13 widget types)
- ✅ Optional multi-hop search fields
- ✅ Flexible metadata dict
- ✅ Dismissible flag for UI interaction

**Mistakes Found**: None

**Behavioral Notes**:
- All fields are optional except id, type, timestamp
- Multi-hop fields (progress, hops, citations) are optional
- Literal type ensures only valid widget types

**Dependencies**:
- **Used by**: All UI widgets throughout the system
- **Re-exported from**: `models/schemas.py` (deprecated alias)
- **Re-exported from**: `api/models.py` (deprecated alias)

**Reusability**: HIGH - Core domain entity pattern

---

## File Summary

**Total Classes**: 1
**Total Functions**: 0
**Lines of Code**: 53

**Violations**: None

**Success Patterns**:
- ✅ Canonical domain entity location
- ✅ Literal type constraint for widget types
- ✅ Optional multi-hop search fields
- ✅ Flexible metadata for extensions
- ✅ Clear docstring explaining purpose

**Overall Assessment**: EXCELLENT - Perfect example of DDD domain entity.

**Key Learnings for Real AgentX**:
1. ✅ **Domain Entities**: Belong in `domain/entities/`, not `api/` or `services/`
2. ✅ **Literal Types**: Use `Literal` for constrained string values
3. ✅ **Optional Fields**: Use `| None = None` for optional fields
4. ✅ **Flexible Metadata**: `dict[str, Any]` allows extensions
5. ✅ **Single Source of Truth**: One canonical location, re-export elsewhere

**Reuse for Real AgentX**: ✅ REQUIRED - Follow this domain entity pattern.
