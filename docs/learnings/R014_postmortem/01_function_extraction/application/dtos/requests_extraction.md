# Function Postmortem: application/dtos/requests.py

## Metadata
- **File**: application/dtos/requests.py
- **Lines of Code**: 84
- **Purpose**: Request DTOs for API layer (Clean Architecture)
- **Dependencies**: `pydantic`, `typing`

---

## Analysis

**File Status**: CLEAN ARCHITECTURE DTO LAYER

**Purpose**: Data Transfer Objects for API requests following Clean Architecture principles. DTOs define the contract between the API layer and application layer.

---

## Classes Extracted

### GenerateWidgetRequest

**Purpose**: Request schema for simple widget generation

**Signature**:
```python
class GenerateWidgetRequest(BaseModel):
```

**Lines**: 12-30

**Fields**:
```python
class GenerateWidgetRequest(BaseModel):
    """Request to generate content."""

    prompt: str
    widget_type: (
        Literal[
            "markdown",
            "card",
            "form",
            "progress",
            "action",
            "confirmation",
            "image",
            "gallery",
            "chart",
        ]
        | None
    ) = None
```

**What Works**:
- ✅ Literal type constraint (9 widget types)
- ✅ Optional widget_type (LLM can decide)
- ✅ Clear prompt field
- ✅ Pydantic validation

**Mistakes Found**: None

**Reusability**: HIGH - Standard request DTO pattern

---

### IntelligentGenerateRequest

**Purpose**: Request for intelligent UI generation with device context

**Signature**:
```python
class IntelligentGenerateRequest(BaseModel):
```

**Lines**: 32-41

**Fields**:
```python
class IntelligentGenerateRequest(BaseModel):
    """Request for intelligent UI generation with device context."""

    prompt: str
    device_context: dict[str, Any] = {
        "type": "desktop",
        "screen_width": 1920,
        "screen_height": 1080,
    }
```

**What Works**:
- ✅ Device context for responsive UI
- ✅ Sensible defaults (desktop, 1920x1080)
- ✅ Flexible dict for context

**Mistakes Found**:
- ⚠️ Mutable default argument (`dict[str, Any] = {...}`)
- **Issue**: Pydantic v2 handles this correctly, but it's an anti-pattern in plain Python
- **Risk**: Could cause issues if not using Pydantic

**Reusability**: HIGH - Device context pattern for responsive UI

---

### SearchRequest

**Purpose**: Request for multi-hop search

**Signature**:
```python
class SearchRequest(BaseModel):
```

**Lines**: 43-54

**Fields**:
```python
class SearchRequest(BaseModel):
    """Request for multi-hop search."""

    query: str = Field(..., min_length=1, description="User's search query")
    session_id: str | None = Field(None, description="Optional session identifier")
    max_hops: int | None = Field(
        None, ge=1, le=10, description="Maximum hops (overrides default)"
    )
    enable_citations: bool = Field(
        default=True, description="Include citations in result"
    )
```

**What Works**:
- ✅ Field validation (min_length=1 for query)
- ✅ Range validation (ge=1, le=10 for max_hops)
- ✅ Optional session_id for tracking
- ✅ Boolean flag for citations
- ✅ Clear Field descriptions

**Mistakes Found**: None

**Reusability**: HIGH - Search request pattern with validation

---

### CitationRequest

**Purpose**: Citation from a source document

**Signature**:
```python
class CitationRequest(BaseModel):
```

**Lines**: 56-65

**Fields**:
```python
class CitationRequest(BaseModel):
    """A citation from a source document."""

    cited_text: str = Field(..., description="Text cited from the source")
    document_index: int = Field(
        ..., description="Index of the document in search results"
    )
    document_title: str | None = Field(None, description="Title of the document")
    url: str | None = Field(None, description="URL of the source")
```

**What Works**:
- ✅ Tracks cited text
- ✅ Document index for reference
- ✅ Optional title and URL
- ✅ Clear Field descriptions

**Mistakes Found**: None

**Reusability**: HIGH - Citation pattern for RAG systems

---

### HopEventRequest

**Purpose**: Hop progress event for WebSocket streaming

**Signature**:
```python
class HopEventRequest(BaseModel):
```

**Lines**: 67-84

**Fields**:
```python
class HopEventRequest(BaseModel):
    """Hop progress event for WebSocket streaming."""

    event_type: str = Field(
        ...,
        description="Event type: hop_start, hop_progress, hop_complete, search_complete",
    )
    hop_number: int = Field(..., description="Current hop number (1-indexed)")
    total_hops: int = Field(..., description="Total number of hops")
    message: str = Field(..., description="Human-readable status message")
    progress: float = Field(..., ge=0.0, le=1.0, description="Progress 0.0 to 1.0")
    eta_seconds: float | None = Field(None, description="Estimated time remaining")
    documents_found: int = Field(default=0, description="Number of documents found")
    query_used: str | None = Field(None, description="Search query used")
    reflection_reasoning: str | None = Field(
        None, description="Runtime reflection output"
    )
```

**What Works**:
- ✅ Event type enum (hop_start, hop_progress, hop_complete, search_complete)
- ✅ Hop tracking (current, total)
- ✅ Progress as float 0.0-1.0 (ge=0.0, le=1.0)
- ✅ ETA for UX
- ✅ Documents found count
- ✅ Query used for transparency
- ✅ Reflection reasoning for debugging

**Mistakes Found**:
- ⚠️ event_type is string, not Literal (could be misspelled)
- **Recommendation**: Use `Literal["hop_start", "hop_progress", "hop_complete", "search_complete"]`

**Reusability**: HIGH - WebSocket event pattern for long-running tasks

---

## File Summary

**Total Classes**: 5
**Total Functions**: 0
**Lines of Code**: 84

**Violations**: None

**Success Patterns**:
- ✅ Literal type constraints for enums
- ✅ Field validation with Field() (min_length, ge, le)
- ✅ Clear descriptions in Field()
- ✅ Optional fields with sensible defaults
- ✅ Device context pattern for responsive UI
- ✅ WebSocket event pattern for streaming

**Overall Assessment**: EXCELLENT - Clean DTO layer with proper validation.

**Key Learnings for Real AgentX**:
1. ✅ **DTO Pattern**: Separate request/response schemas from domain entities
2. ✅ **Field Validation**: Use Field() with constraints (min_length, ge, le)
3. ✅ **Literal Types**: Use Literal for string enums
4. ✅ **Device Context**: Include device context for responsive UI
5. ⚠️ **Mutable Defaults**: Avoid mutable defaults in plain Python (Pydantic v2 OK)
6. ⚠️ **Event Types**: Use Literal for event_type instead of str

**Reuse for Real AgentX**: ✅ REQUIRED - Use this DTO pattern for API layer.
