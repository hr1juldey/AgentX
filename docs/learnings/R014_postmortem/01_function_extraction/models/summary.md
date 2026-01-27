# Models Directory Summary

**Directory**: `models/`

**Purpose**: Legacy Pydantic models (DEPRECATED)

---

## Files Extracted

1. **schemas.py** (33 lines) - DEPRECATED
   - ItemCreate (example)
   - ItemResponse (example)
   - ErrorResponse (example)

---

## Status

**DEPRECATED** - Use `application/dtos/` instead.

---

## Migration Pattern

**From (Deprecated)**:
```python
from models.schemas import ItemCreate, ItemResponse
```

**To (Current)**:
```python
from application.dtos.requests import SomeRequest
from application.dtos.responses import SomeResponse
```

---

## Key Learnings

1. Keep schemas in application layer (application/dtos/)
2. Add clear deprecation warnings
3. ErrorResponse pattern is reusable
4. Field validation with Field() (min_length, max_length)

---

## Reusability for Real AgentX

**COPY PATTERN ONLY** - Don't use these directly.

Use `application/dtos/` for all request/response schemas.
