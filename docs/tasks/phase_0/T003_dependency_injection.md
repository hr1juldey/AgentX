# T003: Create Dependency Injection Container

**Phase**: 0
**Estimated Time**: 20 minutes
**Dependencies**: T001, T002
**Blocked By**: None

---

## Context

**LLD References**:
- `lld/application_services.md` - Use cases depend on repositories from DI
- `lld/infrastructure_adapters.md` - Adapter classes to be injected
- Mimicus backend: `src/core/dependencies.py` pattern

**Description**:
Creates dependency injection container following Mimicus pattern with global singletons and getter functions. This pattern is used throughout the application.

---

## Acceptance Criteria

**Passing Criteria**:
- `core/dependencies.py` exists with all getter functions
- Global singletons initialized lazily
- All getter functions return correct types
- Can override for testing (set_* functions)

**Verification Commands**:
```bash
cd /home/riju279/Documents/Code/XRIG/AgentX/prototypes/R013_travel_planning_stream/backend

# Verify file exists
test -f agentx/core/dependencies.py && echo "dependencies.py exists"

# Verify imports work (will fail on stubs, that's OK)
python3 -c "from agentx.core.dependencies import get_settings; print('DI imports work')"
```

---

## Implementation Steps

### Step 1: Create dependencies.py

Create file `agentx/core/dependencies.py`:

```python
"""Dependency injection container with global singletons.

Follows Mimicus backend pattern:
- Global singleton instances (lazy initialized)
- Getter functions to access instances
- Setter functions for testing overrides
"""

from typing import Optional
from fastapi import FastAPI

from agentx.core.config import Settings, get_settings


# ============================================================================
# Global Singletons (Lazy Initialized)
# ============================================================================

_app: Optional[FastAPI] = None
_settings: Optional[Settings] = None


# ============================================================================
# Getter Functions
# ============================================================================

def get_app() -> FastAPI:
    """Get or create the FastAPI application instance.

    Returns:
        FastAPI: The application singleton

    Raises:
        RuntimeError: If app not initialized and no auto-create logic
    """
    global _app
    if _app is None:
        from agentx.main import create_app
        _app = create_app()
    return _app


def get_redis_adapter():
    """Get Redis session adapter instance.

    Returns:
        RedisSessionAdapter: Redis adapter for session storage
    """
    from infrastructure.external.redis_session_adapter import RedisSessionAdapter
    from core.config import get_settings

    settings = get_settings()
    # TODO: Initialize with actual Redis client
    return RedisSessionAdapter(
        redis_client=None,  # Will be initialized
        ttl_seconds=settings.redis_session_ttl_seconds
    )


def get_sqlite_adapter():
    """Get SQLite session adapter instance.

    Returns:
        SQLiteSessionAdapter: SQLite adapter for long-term storage
    """
    from infrastructure.external.sqlite_session_adapter import SQLiteSessionAdapter
    from core.config import get_settings

    settings = get_settings()
    return SQLiteSessionAdapter(db_path=settings.sqlite_db_path)


def get_qdrant_adapter():
    """Get Qdrant vector store adapter instance.

    Returns:
        QdrantVectorStoreAdapter: Qdrant adapter for vector storage
    """
    from infrastructure.external.qdrant_vector_store import QdrantVectorStoreAdapter
    from core.config import get_settings

    settings = get_settings()
    # TODO: Initialize with actual Qdrant client
    return QdrantVectorStoreAdapter(
        client=None,  # Will be initialized
        collection_name=settings.qdrant_collection_name
    )


def get_ollama_adapter():
    """Get Ollama LLM adapter instance.

    Returns:
        OllamaLLMAdapter: Ollama adapter for LLM inference
    """
    from infrastructure.external.ollama_llm import OllamaLLMAdapter
    from core.config import get_settings

    settings = get_settings()
    return OllamaLLMAdapter(
        base_url=settings.ollama_base_url,
        model=settings.ollama_model,
        timeout_seconds=settings.ollama_timeout_seconds
    )


def get_websocket_manager():
    """Get WebSocket manager instance.

    Returns:
        WebSocketManager: WebSocket manager for streaming
    """
    from infrastructure.external.websocket_manager import WebSocketManager
    return WebSocketManager()


# ============================================================================
# Session Repository Factory
# ============================================================================

def get_session_repository():
    """Get session repository (Redis for active, SQLite fallback).

    Returns:
        AgentSessionRepository: Session repository instance
    """
    from domain.repositories.agent_session_repository import AgentSessionRepository

    # Try Redis first, fall back to SQLite
    try:
        return get_redis_adapter()
    except Exception:
        return get_sqlite_adapter()


# ============================================================================
# Setter Functions (For Testing)
# ============================================================================

def set_app(app: FastAPI) -> None:
    """Override the global app instance (for testing).

    Args:
        app: FastAPI app instance to set
    """
    global _app
    _app = app


def set_settings(settings: Settings) -> None:
    """Override the global settings instance (for testing).

    Args:
        settings: Settings instance to set
    """
    global _settings
    _settings = settings
```

### Step 2: Update core/__init__.py

Add to `agentx/core/__init__.py`:

```python
"""Core layer: Configuration and dependency injection."""

from agentx.core.config import Settings, get_settings
from agentx.core.dependencies import (
    get_app,
    get_redis_adapter,
    get_sqlite_adapter,
    get_qdrant_adapter,
    get_ollama_adapter,
    get_websocket_manager,
    get_session_repository,
    set_app,
    set_settings,
)

__all__ = [
    "Settings",
    "get_settings",
    "get_app",
    "get_redis_adapter",
    "get_sqlite_adapter",
    "get_qdrant_adapter",
    "get_ollama_adapter",
    "get_websocket_manager",
    "get_session_repository",
    "set_app",
    "set_settings",
]
```

---

## Expected Failures & Countermeasures

### Failure: ImportError for infrastructure modules

**Likelihood**: High (expected during Phase 0)
**Symptoms**: `ModuleNotFoundError: No module named 'infrastructure.external.redis_session_adapter'`

**Countermeasures**:
1. This is EXPECTED in Phase 0 - adapters not created yet
2. Import will work after Phase 1 when adapters are implemented
3. For now, imports may fail but structure is correct

**Recovery Time**: 0 minutes (expected failure)

### Failure: Circular import

**Likelihood**: Low
**Symptoms**: `ImportError: cannot import name 'X' from partially initialized module`

**Countermeasures**:
1. Move imports inside getter functions (already done)
2. Ensure get_settings() doesn't import from other layers
3. Check that main.py doesn't import dependencies at module level

**Recovery Time**: 10 minutes

---

## Retroactive Measures

### Upstream Drift Recovery

**Scenario**: T002 Settings changed field names
**Detection**: Settings.get_settings() fails
**Action**: Update any hardcoded field names in getter functions

**Recovery Time**: 5 minutes

### Downstream Impact

**Scenario**: Getter function signatures change
**Prevention**: Function signatures are LOCKED after this task
**Mitigation**: If changes needed, update all use sites
**Affected Tasks**: T006 (App Factory), all Phase 1+ tasks using repositories

---

## Artifacts

**Files Created**:
- `agentx/core/dependencies.py` (DI container, not locked)

**Files Modified**:
- `agentx/core/__init__.py` (Add exports, not locked)

**Locked APIs**:
- All getter function names: `get_app()`, `get_settings()`, etc.
- All setter function names: `set_app()`, `set_settings()`

---

## Quality Gates

**Quality Checks**:
- **Check**: dependencies.py can be imported
  - Command: `python3 -c "from agentx.core.dependencies import get_settings; print('OK')"`
  - Expected: `OK`
  - Required: Yes

- **Check**: Core __init__.py exports are correct
  - Command: `python3 -c "from agentx.core import get_settings; print('OK')"`
  - Expected: `OK`
  - Required: Yes

---

## Notes

1. Getter functions that import from infrastructure will fail during Phase 0
2. This is EXPECTED and will be fixed in Phase 1 when adapters are created
3. All getter/setter function names are LOCKED after this task
4. Use `get_*()` pattern for all dependency access
5. Use `set_*()` functions only in tests, not in production code

---

## Completion Checklist

- [ ] agentx/core/dependencies.py created
- [ ] All getter functions defined
- [ ] All setter functions defined
- [ ] core/__init__.py updated with exports
- [ ] Import test passes (for core functions)
- [ ] Ready for T004 (CORS Middleware)

---

**Task T003 is part of Phase 0: Minimal System**
**Locked API**: All getter/setter function signatures
