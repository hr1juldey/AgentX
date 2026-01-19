# T006: Create FastAPI Application Factory

**Phase**: 0
**Estimated Time**: 25 minutes
**Dependencies**: T001, T002, T003, T004, T005
**Blocked By**: None

---

## Context

**LLD References**:
- `lld/incremental_release_plan.md` - Phase 0: FastAPI server setup
- Mimicus backend: `src/core/app.py` pattern

**Description**:
Creates FastAPI application factory function that sets up middleware, routes, and error handlers. This is the main entry point pattern.

---

## Acceptance Criteria

**Passing Criteria**:
- `main.py` exists with `create_app()` factory function
- CORS middleware applied
- Logging middleware applied
- Health endpoint registered
- Server can start without errors

**Verification Commands**:
```bash
cd /home/riju279/Documents/Code/XRIG/AgentX/prototypes/R013_travel_planning_stream/backend

# Verify file exists
test -f agentx/main.py && echo "main.py exists"

# Verify app can be created
python3 -c "from agentx.main import create_app; app = create_app(); print('App created successfully')"
```

---

## Implementation Steps

### Step 1: Create FastAPI application factory

Create file `agentx/main.py`:

```python
"""FastAPI application factory and entry point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from starlette.middleware.errors import ServerErrorMiddleware

from agentx.core.config import Settings, get_settings
from agentx.core.middleware.cors import get_cors_middleware
from agentx.core.middleware.logging import RequestLoggingMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager.

    Args:
        app: FastAPI application instance
    """
    # Startup
    print("AGENTX starting up...")
    yield
    # Shutdown
    print("AGENTX shutting down...")


def create_app() -> FastAPI:
    """Create and configure FastAPI application.

    This is the main application factory.
    All middleware and routes are registered here.

    Returns:
        FastAPI: Configured application instance

    Example:
        >>> from agentx.main import create_app
        >>> app = create_app()
    """
    settings = get_settings()

    # Create FastAPI app
    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        debug=settings.debug,
        lifespan=lifespan,
    )

    # Add CORS middleware (must be first)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add logging middleware
    app.add_middleware(RequestLoggingMiddleware)

    # Add error handling middleware
    app.add_middleware(ServerErrorMiddleware, debug=app.debug)

    # Register exception handlers
    _register_exception_handlers(app)

    # Register routes
    _register_routes(app)

    return app


def _register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers.

    Args:
        app: FastAPI application instance
    """

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        """Handle Pydantic validation errors."""
        from fastapi.responses import JSONResponse

        return JSONResponse(
            status_code=422,
            content={
                "detail": exc.errors(),
                "body": exc.body,
            },
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc):
        """Handle HTTP exceptions."""
        from fastapi.responses import JSONResponse

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc):
        """Handle all unhandled exceptions."""
        from fastapi.responses import JSONResponse
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Unhandled exception: {exc}", exc_info=True)

        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
            },
        )


def _register_routes(app: FastAPI) -> None:
    """Register all routes.

    Args:
        app: FastAPI application instance
    """
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "app_name": get_settings().app_name,
            "version": get_settings().version,
        }

    # API v1 routes (placeholder)
    @app.get("/api/v1/")
    async def api_v1_root():
        """API v1 root endpoint."""
        return {
            "message": "AGENTX API v1",
            "version": get_settings().version,
        }


# For development: allow running this file directly
if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    app = create_app()

    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
    )
```

### Step 2: Create empty conftest.py for tests

Create file `tests/conftest.py`:

```python
"""Pytest configuration and fixtures."""

import pytest
from agentx.main import create_app
from agentx.core.config import Settings, set_settings


@pytest.fixture
def app():
    """FastAPI app fixture for testing."""
    return create_app()


@pytest.fixture
def settings():
    """Settings fixture for testing."""
    test_settings = Settings(
        app_name="AGENTX-Test",
        environment="testing",
        port=8001,
        redis_host="localhost",
        redis_port=6379,
        qdrant_url="http://localhost:6333",
    )
    set_settings(test_settings)
    return test_settings
```

---

## Expected Failures & Countermeasures

### Failure: Import errors for middleware

**Likelihood**: Low (T004/T005 created them)
**Symptoms**: `ModuleNotFoundError: No module named 'agentx.core.middleware'`

**Countermeasures**:
1. Ensure T004 and T005 are complete
2. Check middleware/__init__.py exports are correct

**Recovery Time**: 2 minutes

### Failure: Uvicorn not installed

**Likelihood**: Medium
**Symptoms**: `ModuleNotFoundError: No module named 'uvicorn'`

**Countermeasures**:
1. Install uvicorn: `uv add uvicorn[standard]`
2. Or use pip: `pip install uvicorn[standard]`

**Recovery Time**: 3 minutes

---

## Retroactive Measures

### Upstream Drift Recovery

**Scenario**: T002/T003/T004/T005 changed
**Detection**: Import errors in main.py
**Action**: Re-run affected tasks to ensure consistency

**Recovery Time**: 10 minutes

### Downstream Impact

**Scenario**: App factory signature changes
**Prevention**: `create_app()` signature is LOCKED
**Mitigation**: If changes needed, update all use sites
**Affected Tasks**: All tasks that create FastAPI apps

---

## Artifacts

**Files Created**:
- `agentx/main.py` (App factory, not locked)
- `tests/conftest.py` (Pytest fixtures, not locked)

**Locked APIs**:
- `create_app()` function signature (no parameters)
- `lifespan()` async context manager pattern
- Exception handler names and signatures

---

## Quality Gates

**Quality Checks**:
- **Check**: App can be imported
  - Command: `python3 -c "from agentx.main import create_app; print('OK')"`
  - Expected: `OK`
  - Required: Yes

- **Check**: App can be created
  - Command: `python3 -c "from agentx.main import create_app; app = create_app(); print(f'{app.title} v{app.version}')"`
  - Expected: `AGENTX v1.0.0`
  - Required: Yes

- **Check**: Tests can import fixtures
  - Command: `python3 -c "from tests.conftest import app; print('OK')"`
  - Expected: `OK`
  - Required: Yes

---

## Notes

1. Direct execution (`python main.py`) works for development
2. Production should use uvicorn/gunicorn with `agentx.main:create_app`
3. Middleware order matters: CORS first, then logging
4. Exception handlers provide consistent error responses
5. Health endpoint returns JSON with status info

---

## Completion Checklist

- [ ] agentx/main.py created
- [ ] create_app() factory function implemented
- [ ] lifespan() context manager implemented
- [ ] Exception handlers registered
- [ ] Health endpoint registered
- [ ] tests/conftest.py created
- [ ] Import tests pass
- [ ] App creation test passes
- [ ] Ready for T007 (Health Endpoint - already done)
- [ ] Ready for T008 (Stub Repositories)

---

**Task T006 is part of Phase 0: Minimal System**
**Locked API**: create_app() function signature
