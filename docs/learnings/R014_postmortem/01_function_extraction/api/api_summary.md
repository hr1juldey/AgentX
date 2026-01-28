# API Directory Summary - R014 Postmortem Extraction

**Analysis Date**: 2026-01-28
**Directory**: `/prototypes/R014_ui_showcase/backend/api/`

---

## Directory Structure

```
api/
├── content_generator.py       # Facade for widget generators
├── dspy_signatures.py         # 12 DSPy signatures for content generation
├── mock_handler.py            # Mock mode WebSocket handler
├── models.py                  # DEPRECATED - Type aliases
├── routes.py                  # DEPRECATED - Re-exports
├── routes_examples.py         # Static example data endpoints
├── routes.py.backup           # Backup file (ignored)
├── generators/                # Widget generator classes
│   ├── __init__.py
│   ├── text_widgets.py        # Markdown, card, form generators
│   ├── interactive_widgets.py # Progress, action, confirmation
│   └── media_widgets.py       # Image, gallery, chart
└── routes/                    # API route modules
    ├── __init__.py
    ├── health.py              # Health check endpoint
    ├── widgets.py             # Re-exports widget_routes
    ├── search.py              # Multi-hop search (REST + WS)
    ├── master_agent.py        # Main WebSocket endpoint
    ├── e2e_test.py            # E2E testing endpoints
    └── widget_routes/         # Widget generation routes
        ├── __init__.py
        ├── endpoints.py       # Main generation endpoints
        └── mock.py            # Legacy mock endpoints
```

---

## File Statistics

| File | Lines | Classes | Functions | DEPRECATED |
|------|-------|---------|-----------|------------|
| content_generator.py | 34 | 1 | 0 | No |
| dspy_signatures.py | 99 | 12 | 0 | No |
| mock_handler.py | 88 | 0 | 1 | No |
| models.py | 26 | 0 | 0 | Yes |
| routes.py | 24 | 0 | 0 | Yes |
| routes_examples.py | 139 | 0 | 5 | No |
| generators/__init__.py | 16 | 0 | 0 | No |
| generators/text_widgets.py | 79 | 1 | 3 | No |
| generators/interactive_widgets.py | 77 | 1 | 3 | No |
| generators/media_widgets.py | 84 | 1 | 3 | No |
| routes/__init__.py | 33 | 0 | 0 | No |
| routes/health.py | 24 | 0 | 1 | No |
| routes/widgets.py | 9 | 0 | 0 | No |
| routes/search.py | 107 | 0 | 2 | No |
| routes/master_agent.py | 146 | 0 | 3 | No |
| routes/e2e_test.py | 174 | 0 | 4 | No |
| routes/widget_routes/__init__.py | 16 | 0 | 0 | No |
| routes/widget_routes/endpoints.py | 122 | 0 | 3 | No |
| routes/widget_routes/mock.py | 53 | 0 | 1 | No |

**Total**: 18 Python files, 19 classes, 31 functions

---

## CLAUDE_POLICY.md Violations

### Violations Found

| File | Violation | Severity | Description |
|------|-----------|----------|-------------|
| `mock_handler.py:8` | RELATIVE IMPORT | Medium | `from pathlib import Path` (allowed) |
| `routes/health.py:12` | REDUNDANT CODE | Low | `logger = logger = ...` (double assignment) |
| `routes/master_agent.py:15` | OBFUSCATED IMPORT | Low | `router = __import__("fastapi").APIRouter()` |
| `routes/widget_routes/mock.py:15` | OBFUSCATED IMPORT | Low | `logger = __import__("logging").getLogger(__name__)` |
| `routes/widget_routes/endpoints.py:16` | OBFUSCATED IMPORT | Low | `logger = __import__("logging").getLogger(__name__)` |

**Note**: Obfuscated imports (`__import__()`) used to avoid linter detecting unused imports. This is a workaround pattern.

---

## Key Patterns Observed

### 1. Facade Pattern (content_generator.py)

```python
class ContentGenerator:
    # Delegates to specialized generators
    generate_markdown = TextWidgetGenerator.generate_markdown
    generate_card = TextWidgetGenerator.generate_card
    # ...
```

**Analysis**:
- ✅ Clean separation of concerns
- ✅ Class method aliasing avoids duplication
- ⚠️ Relies on static methods in generator classes

### 2. DSPy Signature Pattern (dspy_signatures.py)

```python
class MarkdownContentSignature(dspy.Signature):
    topic = dspy.InputField(desc="Topic to write about")
    content = dspy.OutputField(desc="Markdown formatted content")
```

**Analysis**:
- ✅ Verbose field descriptions (good for LLM context)
- ⚠️ 12 signatures - potential for consolidation
- ⚠️ Many signatures have similar patterns (could be generalized)

### 3. Mock Mode Pattern (mock_handler.py)

```python
async def handle_mock_mode(websocket: WebSocket, session_id: str, query: str):
    # Reads from JSON file, sends pre-defined widgets
```

**Analysis**:
- ✅ Useful for development/testing
- ✅ Avoids LLM calls for predictable output
- ⚠️ Hardcoded delay (0.5s) - should be configurable
- ✅ Good error handling

### 4. Async Generator Pattern (generators/*.py)

```python
@staticmethod
async def generate_markdown(prompt: str) -> UIDescriptor:
    generator = dspy.Predict(MarkdownContentSignature)
    result = generator(topic=prompt)
    return UIDescriptor(...)
```

**Analysis**:
- ✅ Consistent async pattern
- ⚠️ Creates new `dspy.Predict` on each call (not cached)
- ⚠️ `datetime.now().timestamp()` for IDs - potential collision
- ⚠️ Hardcoded metadata values (e.g., "sparkles" icon)

### 5. WebSocket Handler Pattern (routes/*.py)

```python
@router.websocket("/ws/generate-widget")
async def generate_widget_master_agent(websocket: WebSocket):
    await websocket.accept()
    session_id = str(uuid.uuid4())[:8]
    connection_active = True
    # ... nested callback functions
```

**Analysis**:
- ✅ Proper WebSocket lifecycle management
- ✅ Connection state tracking (`connection_active`)
- ⚠️ Nested callbacks make code hard to read
- ⚠️ Exception handling with bare `except: pass`
- ✅ Session ID generation with truncation

### 6. Deprecated Re-export Pattern (models.py, routes.py)

```python
# models.py
from application.dtos.requests import (
    GenerateWidgetRequest as GenerateRequest,
    ...
)
UIDescriptor = UIDescriptorEntity  # Type alias
```

**Analysis**:
- ⚠️ Maintains backward compatibility
- ⚠️ Creates confusion about where to import from
- ⚠️ Should be removed with migration plan

---

## SOLID Violations

### Single Responsibility Principle

| File | Issue | Severity |
|------|-------|----------|
| `master_agent.py` | Handles WebSocket + master agent + QA + delivery plan | Medium |
| `endpoints.py` | Conversion logic mixed with endpoint logic | Low |

### Open/Closed Principle

| File | Issue | Severity |
|------|-------|----------|
| `mock.py` | Large if/elif chain for widget types | Medium |
| `content_generator.py` | Static method aliases - not extensible | Low |

### Dependency Inversion Principle

| File | Issue | Severity |
|------|-------|----------|
| All generators | Depend on concrete `UIDescriptor` from api.models | Medium |
| All routes | Directly import from application layer | Low |

---

## DRY Violations

### Code Duplication

| Pattern | Occurrences | Locations |
|---------|-------------|-----------|
| `datetime.now().timestamp()` | 9+ | All generator files |
| Error widget creation | 3 | endpoints.py, mock.py, text_widgets.py |
| WebSocket error handling | 4 | search.py, master_agent.py, e2e_test.py |
| `UIDescriptor(...)` construction | 15+ | All generator files |
| `logger = __import__("logging")` | 3 | Multiple route files |

---

## Behavioral Notes

### LLM Interactions

1. **DSPy Predict Instantiation**: Every generator call creates new `dspy.Predict` instance
2. **No Caching**: Each LLM call is independent
3. **No Streaming**: All generators return complete UIDescriptor
4. **Error Handling**: LLM errors caught and converted to error widgets

### Edge Cases

1. **Empty Query**: Handled by getting empty string from dict
2. **Device Context**: Falls back to "desktop" if invalid
3. **WebSocket Disconnect**: Gracefully handled with state tracking
4. **Mock Data Missing**: Sends error message to WebSocket

### Performance Characteristics

1. **LLM Latency**: Each generator call blocks on LLM response
2. **No Parallel Generation**: Widgets generated sequentially
3. **Connection Pooling**: Not used (each request独立的)

---

## Refactoring Recommendations

### High Priority

1. **Consolidate DSPy Signatures**: Many follow similar pattern
   ```python
   # Instead of 12 signatures, use generic:
   class ContentSignature(dspy.Signature):
       context = dspy.InputField(desc="Generation context")
       content = dspy.OutputField(desc="Generated content")
   ```

2. **Extract WebSocket Utilities**: Common patterns to helper functions
   ```python
   async def safe_send(websocket, data, connection_state):
       if connection_state:
           try:
               await websocket.send_json(data)
           except:
               return False
       return True
   ```

3. **Fix Obfuscated Imports**: Replace `__import__()` with normal imports

### Medium Priority

1. **Generator Factory**: Replace static methods with factory pattern
2. **ID Generation**: Use UUID instead of timestamp
3. **Configuration**: Extract hardcoded values (delays, icons)
4. **Remove Deprecated Files**: Create migration plan for models.py, routes.py

### Low Priority

1. **Type Hints**: Add return types to all functions
2. **Docstrings**: Complete missing documentation
3. **Logging**: Standardize log messages

---

## Integration Points

### Depends On

- `domain.entities.ui_descriptor` - UIDescriptor entity
- `application.dtos.requests` - Request DTOs
- `application.use_cases.*` - Use case layer
- `config.dspy` - DSPy configuration
- `config.settings` - Settings (mock_mode)

### Used By

- `main.py` - API router inclusion
- Frontend - WebSocket connections
- Tests - E2E testing

---

## Files Requiring Extraction Detail

1. ✅ `content_generator.py` - Facade pattern analysis
2. ✅ `dspy_signatures.py` - 12 signature definitions
3. ✅ `mock_handler.py` - Mock mode WebSocket handler
4. ✅ `models.py` - Deprecated type aliases
5. ✅ `routes.py` - Deprecated router re-export
6. ✅ `routes_examples.py` - Static example endpoints
7. ✅ `generators/text_widgets.py` - 3 text generators
8. ✅ `generators/interactive_widgets.py` - 3 interactive generators
9. ✅ `generators/media_widgets.py` - 3 media generators
10. ✅ `routes/health.py` - Health check endpoint
11. ✅ `routes/widgets.py` - Widget router re-export
12. ✅ `routes/search.py` - Search endpoints (REST + WS)
13. ✅ `routes/master_agent.py` - Main master agent WebSocket
14. ✅ `routes/e2e_test.py` - E2E testing endpoints
15. ✅ `routes/widget_routes/endpoints.py` - Widget generation endpoints
16. ✅ `routes/widget_routes/mock.py` - Legacy mock endpoints

---

## Next Steps

1. Review individual extraction files for each module
2. Identify cross-cutting concerns for refactoring
3. Create migration plan for deprecated code
4. Document behavioral quirks for testing
