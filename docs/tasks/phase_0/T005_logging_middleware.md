# T005: Create Logging Middleware

**Phase**: 0
**Estimated Time**: 20 minutes
**Dependencies**: T001, T002
**Blocked By**: None

---

## Context

**LLD References**:
- `lld/incremental_release_plan.md` - Phase 0: Logging middleware
- FastAPI middleware documentation

**Description**:
Creates request logging middleware for tracking all HTTP requests. Supports JSON and text log formats from settings.

---

## Acceptance Criteria

**Passing Criteria**:
- `core/middleware/logging.py` exists with logging middleware
- Logs request method, path, status code, duration
- Format configurable (json/text)
- Sensitive data (PII) not logged

**Verification Commands**:
```bash
cd /home/riju279/Documents/Code/XRIG/AgentX/prototypes/R013_travel_planning_stream/backend

# Verify file exists
test -f agentx/core/middleware/logging.py && echo "logging.py exists"

# Verify import works
python3 -c "from agentx.core.middleware.logging import RequestLoggingMiddleware; print('OK')"
```

---

## Implementation Steps

### Step 1: Create logging middleware

Create file `agentx/core/middleware/logging.py`:

```python
"""Request logging middleware."""

import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from agentx.core.config import get_settings


# Configure root logger
settings = get_settings()
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests and responses."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        """Process request and log details.

        Args:
            request: Incoming request
            call_next: Next middleware/route handler

        Returns:
            Response: Response from handler
        """
        start_time = time.time()

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000

        # Log request
        self._log_request(request, response, duration_ms)

        return response

    def _log_request(
        self,
        request: Request,
        response: Response,
        duration_ms: float,
    ) -> None:
        """Log request details (PII-safe).

        Args:
            request: The request object
            response: The response object
            duration_ms: Request duration in milliseconds
        """
        # Extract request info
        method = request.method
        path = request.url.path
        status_code = response.status_code

        # Create log entry (PII-safe: no query params, no headers)
        log_entry = {
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": round(duration_ms, 2),
        }

        # Log based on format setting
        if settings.log_format == "json":
            logger.info(json.dumps(log_entry))
        else:
            logger.info(
                f"{method} {path} -> {status_code} ({duration_ms:.2f}ms)"
            )


import json  # For JSON logging
```

### Step 2: Update middleware __init__.py

Update `agentx/core/middleware/__init__.py`:

```python
"""Core middleware package."""

from agentx.core.middleware.cors import get_cors_middleware
from agentx.core.middleware.logging import RequestLoggingMiddleware

__all__ = ["get_cors_middleware", "RequestLoggingMiddleware"]
```

---

## Expected Failures & Countermeasures

### Failure: Module 'json' not found

**Likelihood**: Low (json is built-in)
**Symptoms**: `ModuleNotFoundError: No module named 'json'`

**Countermeasures**:
1. Remove `import json` line (built-in, no import needed)
2. Move import to top of file if misplaced

**Recovery Time**: 1 minute

---

## Retroactive Measures

### Upstream Drift Recovery

**Scenario**: T002 Settings.log_format renamed
**Detection**: AttributeError when accessing settings.log_format
**Action**: Update field name in _log_request()

**Recovery Time**: 2 minutes

### Downstream Impact

**Scenario**: Logging format changes
**Prevention**: Settings field names are LOCKED
**Mitigation**: Update _log_request() if needed
**Affected Tasks**: T006 (App Factory)

---

## Artifacts

**Files Created**:
- `agentx/core/middleware/logging.py` (Logging middleware, not locked)

**Files Modified**:
- `agentx/core/middleware/__init__.py` (Add export)

**Locked APIs**:
- `RequestLoggingMiddleware` class name and interface

---

## Quality Gates

**Quality Checks**:
- **Check**: Import works
  - Command: `python3 -c "from agentx.core.middleware.logging import RequestLoggingMiddleware; print('OK')"`
  - Expected: `OK`
  - Required: Yes

---

## Notes

1. Query parameters NOT logged (may contain PII)
2. Headers NOT logged (may contain tokens)
3. Body NOT logged (may contain sensitive data)
4. JSON format useful for log aggregation (ELK, Loki)
5. Text format useful for local development

---

## Completion Checklist

- [ ] agentx/core/middleware/logging.py created
- [ ] RequestLoggingMiddleware class implemented
- [ ] _log_request() PII-safe
- [ ] middleware/__init__.py updated
- [ ] Import test passes
- [ ] Ready for T006 (App Factory)

---

**Task T005 is part of Phase 0: Minimal System**
