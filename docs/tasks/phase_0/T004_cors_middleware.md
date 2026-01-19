# T004: Create CORS Middleware

**Phase**: 0
**Estimated Time**: 15 minutes
**Dependencies**: T001, T002
**Blocked By**: None

---

## Context

**LLD References**:
- `lld/incremental_release_plan.md` - Phase 0: CORS middleware
- FastAPI CORS middleware documentation

**Description**:
Creates CORS middleware for cross-origin requests from frontend. Supports configurable origins from settings.

---

## Acceptance Criteria

**Passing Criteria**:
- `core/middleware/cors.py` exists with CORSMiddleware factory
- CORS origins loaded from Settings
- Middleware applies to all routes
- Credentials allowed for WebSocket

**Verification Commands**:
```bash
cd /home/riju279/Documents/Code/XRIG/AgentX/prototypes/R013_travel_planning_stream/backend

# Verify file exists
test -f agentx/core/middleware/cors.py && echo "cors.py exists"

# Verify import works
python3 -c "from agentx.core.middleware.cors import get_cors_middleware; print('OK')"
```

---

## Implementation Steps

### Step 1: Create CORS middleware

Create file `agentx/core/middleware/cors.py`:

```python
"""CORS middleware configuration."""

from fastapi.middleware.cors import CORSMiddleware

from agentx.core.config import get_settings


def get_cors_middleware() -> CORSMiddleware:
    """Create CORS middleware with settings from configuration.

    Returns:
        CORSMiddleware: Configured CORS middleware

    Example:
        >>> app = FastAPI()
        >>> app.add_middleware(CORSMiddleware, get_cors_middleware())
    """
    settings = get_settings()

    return CORSMiddleware(
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )
```

### Step 2: Update middleware __init__.py

Create file `agentx/core/middleware/__init__.py`:

```python
"""Core middleware package."""

from agentx.core.middleware.cors import get_cors_middleware

__all__ = ["get_cors_middleware"]
```

---

## Expected Failures & Countermeasures

### Failure: Settings.cors_origins is not valid list

**Likelihood**: Low
**Symptoms**: CORS validation error

**Countermeasures**:
1. Check .env file has JSON format for CORS_ORIGINS
2. Ensure list uses double quotes: `["http://localhost:3000"]`
3. Update .env if format is wrong

**Recovery Time**: 3 minutes

---

## Retroactive Measures

### Upstream Drift Recovery

**Scenario**: T002 Settings.cors_origins field renamed
**Detection**: Import error or AttributeError
**Action**: Update field name in get_cors_middleware()

**Recovery Time**: 2 minutes

### Downstream Impact

**Scenario**: Middleware configuration changes
**Prevention**: get_cors_middleware() function signature is LOCKED
**Mitigation**: If changes needed, update T006 (App Factory)
**Affected Tasks**: T006 (App Factory)

---

## Artifacts

**Files Created**:
- `agentx/core/middleware/cors.py` (CORS middleware, not locked)
- `agentx/core/middleware/__init__.py` (Package marker, not locked)

**Locked APIs**:
- `get_cors_middleware()` function signature

---

## Quality Gates

**Quality Checks**:
- **Check**: Import works
  - Command: `python3 -c "from agentx.core.middleware import get_cors_middleware; print('OK')"`
  - Expected: `OK`
  - Required: Yes

---

## Notes

1. CORS origins loaded from Settings (configurable)
2. Credentials enabled for WebSocket support
3. All methods and headers allowed (can be restricted later)
4. Middleware applied in T006 (App Factory)

---

## Completion Checklist

- [ ] agentx/core/middleware/cors.py created
- [ ] agentx/core/middleware/__init__.py created
- [ ] get_cors_middleware() function implemented
- [ ] Import test passes
- [ ] Ready for T005 (Logging Middleware)

---

**Task T004 is part of Phase 0: Minimal System**
