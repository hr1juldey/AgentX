# Function Postmortem: services/multihop_search/schemas.py

## Metadata
- **File**: services/multihop_search/schemas.py
- **Lines of Code**: 79
- **Purpose**: Pydantic models for API requests/responses and internal data structures
- **Dependencies**: `typing`, `pydantic`

---

## Analysis

**File Status**: PRODUCTION PYDANTIC SCHEMAS

**Purpose**: Defines Pydantic models for API contracts (SearchRequest, SearchResult), WebSocket streaming (HopEvent), and citations. Provides type validation and serialization.

---

## Classes Extracted

### Pydantic Models

**`class Citation(BaseModel)`**
- **Purpose**: A citation from a source document
- **Fields**:
  - `cited_text: str` - Text cited from the source (required)
  - `document_index: int` - Index of the document in search results (required)
  - `document_title: str | None` - Title of the document (optional)
  - `url: str | None` - URL of the source (optional)

**`class HopEvent(BaseModel)`**
- **Purpose**: Hop progress event for WebSocket streaming
- **Fields**:
  - `event_type: str` - Event type: hop_start, hop_progress, hop_complete, search_complete (required)
  - `hop_number: int` - Current hop number (1-indexed) (required)
  - `total_hops: int` - Total number of hops (required)
  - `message: str` - Human-readable status message (required)
  - `progress: float` - Progress 0.0 to 1.0 (required, validated: `ge=0.0, le=1.0`)
  - `eta_seconds: float | None` - Estimated time remaining (optional)
  - `documents_found: int = 0` - Number of documents found (default 0)
  - `query_used: str | None` - Search query used (optional)
  - `reflection_reasoning: str | None` - Runtime reflection output (optional)

**`class SearchRequest(BaseModel)`**
- **Purpose**: Search request from client
- **Fields**:
  - `query: str` - User's search query (required, validated: `min_length=1`)
  - `session_id: str | None` - Optional session identifier (optional)
  - `max_hops: int | None` - Maximum hops (overrides default) (optional, validated: `ge=1, le=10`)
  - `enable_citations: bool = True` - Include citations in result (default True)

**`class SearchResult(BaseModel)`**
- **Purpose**: Final search result
- **Fields**:
  - `answer: str` - Final synthesized answer (required)
  - `citations: list[Citation] = Field(default_factory=list)` - Source citations (default empty list)
  - `hops: list[dict[str, Any]] = Field(default_factory=list)` - Details of each hop (default empty list)
  - `metadata: dict[str, Any] = Field(default_factory=dict)` - Additional metadata (time, document counts, etc.) (default empty dict)
  - `queries_used: list[str] = Field(default_factory=list)` - All search queries used (default empty list)
  - `final_reflection_reasoning: str | None` - Final reflection on completeness (optional)

---

## File Summary

**Total Classes**: 4 (Pydantic BaseModel)
**Lines of Code**: 79

**Overall Assessment**: Well-structured Pydantic schemas with proper validation. Good use of Field for constraints (min_length, ge, le). Default factories prevent mutable default arguments. Clear separation of concerns (request, result, events, citations).

**Key Learnings for Real AgentX**:
1. ✅ **Field validation**: Pydantic Field with constraints (min_length, ge, le) for input validation
2. ✅ **Default factories**: `default_factory=list` prevents mutable default argument issues
3. ✅ **Optional fields**: Proper use of `| None` for optional data
4. ✅ **WebSocket events**: HopEvent model for streaming progress updates
5. ✅ **API contracts**: SearchRequest/SearchResult define clear API boundaries
6. ✅ **Metadata field**: Flexible dict for extensible metadata
7. ✅ **Type safety**: Pydantic provides runtime validation and serialization
8. ⚠️ **Generic hops field**: `list[dict[str, Any]]` loses type safety

**Reuse for Real AgentX**: ✅ HIGH - Excellent pattern for API schemas. Pydantic validation prevents invalid data. Default factories prevent bugs. Consider making hops field more type-safe with a HopResult model.
