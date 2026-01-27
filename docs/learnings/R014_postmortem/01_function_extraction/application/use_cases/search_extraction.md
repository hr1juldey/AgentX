# Function Postmortem: application/use_cases/search.py

## Metadata
- **File**: application/use_cases/search.py
- **Lines of Code**: 103
- **Purpose**: Search use cases (Clean Architecture facade)
- **Dependencies**: `application.dtos`, `config.settings`, `services.multihop_search.agents`

---

## Analysis

**File Status**: CLEAN ARCHITECTURE USE CASE LAYER

**Purpose**: Use case facades that wrap existing multi-hop search services. Supports both simple and WebSocket streaming modes.

---

## Classes Extracted

### SearchUseCase

**Purpose**: Use case for multi-hop search operations

**Signature**:
```python
class SearchUseCase:
```

**Lines**: 15-35

**Architecture**: Facade pattern over MultiHopSearchAgent

**Note**: Phase 1 thin wrapper - delegates to service. Phase 3 will implement full use case logic.

---

### search

**Purpose**: Execute multi-hop search and return final answer

**Signature**:
```python
async def search(self, request: SearchRequest) -> str:
```

**Lines**: 25-34

**Key Code**:
```python
async def search(self, request: SearchRequest) -> str:
    """Execute multi-hop search and return final answer.

    Phase 1: Delegates to existing service.
    """
    from services.multihop_search.agents import MultiHopSearchAgent

    agent = MultiHopSearchAgent()
    result = await agent(question=request.query)
    return result.answer
```

**What Works**:
- ✅ Facade pattern (delegates to MultiHopSearchAgent)
- ✅ Returns string answer (simple)
- ✅ Async method
- ✅ Lazy import

**Mistakes Found**: None

**Behavioral Notes**:
- Creates MultiHopSearchAgent with defaults
- Passes query from SearchRequest
- Returns only answer (not full result)

**Reusability**: HIGH - Simple search use case pattern

---

### MultiHopSearchWebSocketUseCase

**Purpose**: Use case for multi-hop search with WebSocket streaming

**Signature**:
```python
class MultiHopSearchWebSocketUseCase:
```

**Lines**: 37-79

**Architecture**: Facade pattern over MultiHopSearchAgent with progress callback

---

### search_with_streaming

**Purpose**: Execute multi-hop search with streaming progress updates

**Signature**:
```python
async def search_with_streaming(
    self,
    request: SearchRequest,
    progress_callback: Callable[[dict[str, Any]], None] | None = None,
) -> SearchResultResponse:
```

**Lines**: 43-79

**Complexity**: O(n) where n is number of hops

**Key Code**:
```python
async def search_with_streaming(
    self,
    request: SearchRequest,
    progress_callback: Callable[[dict[str, Any]], None] | None = None,
) -> SearchResultResponse:
    """Execute multi-hop search with streaming progress updates."""
    from services.multihop_search.agents import MultiHopSearchAgent

    agent = MultiHopSearchAgent(
        max_hops=request.max_hops or settings.max_hops,
        progress_callback=progress_callback,
        stop_threshold=settings.stop_threshold,
    )

    result = await agent(question=request.query)

    # Convert citations to dict format
    citations = []
    if result.citations:
        for cit in result.citations:
            if isinstance(cit, dict):
                citations.append(cit)

    return SearchResultResponse(
        answer=result.answer,
        summary=getattr(result, "summary", ""),
        confidence=getattr(result, "confidence", "medium"),
        citations=citations,
        hops=result.hops or [],
        metadata=result.metadata or {},
        queries_used=result.metadata.get("queries_used", [])
        if result.metadata
        else [],
        final_reflection_reasoning=getattr(
            result, "final_reflection_reasoning", None
        ),
    )
```

**What Works**:
- ✅ Progress callback for WebSocket streaming
- ✅ Configurable max_hops (request or settings)
- ✅ Stop threshold from settings
- ✅ Returns SearchResultResponse (not string)
- ✅ Safe citation conversion (isinstance check)
- ✅ getattr with defaults (summary, confidence)
- ✅ Metadata dict for extensibility
- ✅ Queries used for reproducibility

**Mistakes Found**:
- ⚠️ Manual citation conversion (isinstance check)
- **Issue**: Suggests citations may not be consistent type
- **Recommendation**: Ensure citations are always list[dict]

**Behavioral Notes**:
- Creates MultiHopSearchAgent with config
- Passes progress_callback for WebSocket events
- Converts result to SearchResultResponse DTO
- Uses getattr for optional fields (summary, confidence)
- Extracts queries_used from metadata

**Dependencies**:
- **Imports**: MultiHopSearchAgent, settings
- **Called by**: WebSocket routes for streaming
- **Returns**: SearchResultResponse DTO

**Reusability**: HIGH - WebSocket streaming pattern

---

## Functions Extracted

### get_search_use_case

**Purpose**: Singleton getter for dependency injection

**Signature**:
```python
def get_search_use_case() -> SearchUseCase:
```

**Lines**: 86-91

**Key Code**:
```python
# Singleton getter for dependency injection
_search_use_case: SearchUseCase | None = None


def get_search_use_case() -> SearchUseCase:
    """Get singleton instance of SearchUseCase."""
    global _search_use_case
    if _search_use_case is None:
        _search_use_case = SearchUseCase()
    return _search_use_case
```

**What Works**:
- ✅ Singleton pattern
- ✅ Lazy initialization
- ✅ Global variable with type annotation
- ✅ Dependency injection friendly

**Mistakes Found**: None

**Reusability**: HIGH - Singleton getter pattern for DI

---

### get_websocket_search_use_case

**Purpose**: Singleton getter for WebSocket search use case

**Signature**:
```python
def get_websocket_search_use_case() -> MultiHopSearchWebSocketUseCase:
```

**Lines**: 97-102

**Key Code**:
```python
_websocket_search_use_case: MultiHopSearchWebSocketUseCase | None = None


def get_websocket_search_use_case() -> MultiHopSearchWebSocketUseCase:
    """Get singleton instance of MultiHopSearchWebSocketUseCase."""
    global _websocket_search_use_case
    if _websocket_search_use_case is None:
        _websocket_search_use_case = MultiHopSearchWebSocketUseCase()
    return _websocket_search_use_case
```

**What Works**:
- ✅ Singleton pattern
- ✅ Lazy initialization
- ✅ Separate singleton for WebSocket variant
- ✅ Dependency injection friendly

**Mistakes Found**: None

**Reusability**: HIGH - Singleton getter pattern for DI

---

## File Summary

**Total Classes**: 2
**Total Functions**: 2 methods + 2 getters
**Lines of Code**: 103

**Violations**: None

**Success Patterns**:
- ✅ **Dual Use Cases**: Simple (string) + streaming (SearchResultResponse)
- ✅ **Progress Callback**: Callable for WebSocket events
- ✅ **Configurable**: max_hops from request or settings
- ✅ **Safe Conversion**: isinstance checks for citations
- ✅ **getattr Defaults**: Handle optional fields gracefully
- ✅ **Singleton Getters**: Separate for simple and streaming variants

**Overall Assessment**: EXCELLENT - Clean Architecture with WebSocket streaming support.

**Key Learnings for Real AgentX**:
1. ✅ **Dual Use Cases**: Simple vs streaming variants
2. ✅ **Progress Callbacks**: Use Callable for WebSocket events
3. ✅ **Configurable Limits**: Request overrides settings
4. ✅ **Safe Conversion**: isinstance checks for type consistency
5. ✅ **getattr Defaults**: Handle optional result fields
6. ✅ **Separate Singletons**: One per use case variant

**Reuse for Real AgentX**: ✅ REQUIRED - Use this search use case pattern.

---

## Architectural Note

**Two Search Use Cases**:

**1. SearchUseCase** (simple):
- Input: `SearchRequest`
- Output: `str` (just answer)
- Use case: Simple API endpoints
- No progress tracking

**2. MultiHopSearchWebSocketUseCase** (streaming):
- Input: `SearchRequest` + `progress_callback`
- Output: `SearchResultResponse` (full result)
- Use case: WebSocket endpoints
- Real-time progress events

This separation allows simple use cases to remain simple while supporting advanced features when needed.
