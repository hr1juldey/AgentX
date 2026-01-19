# T103: Update Dependency Injection Container

**Phase**: 1
**Estimated Time**: 25 minutes
**Dependencies**: T003, T101, T102
**Blocked By**: None

---

## Context

**LLD References**:
- `lld/infrastructure_adapters.md` - Adapter patterns
- `lld/domain_model.md` - Repository interface usage

**Description**:
Updates the dependency injection container (core/dependencies.py) to include all Phase 1 adapters and repositories. This ensures all adapters can be accessed via the DI pattern.

---

## Acceptance Criteria

**Passing Criteria**:
- All Phase 1 adapters accessible via getter functions
- Qdrant adapter singleton
- Redis adapter singleton (with fallback to SQLite)
- SQLite adapter singleton
- In-memory UI repository singleton
- Ollama adapter singleton
- All getter functions return initialized adapters

**Verification Commands**:
```bash
cd /home/riju279/Documents/Code/XRIG/AgentX/prototypes/R013_travel_planning_stream/backend

# Verify updated file exists
test -f agentx/core/dependencies.py && echo "dependencies.py exists"

# Verify imports work
python3 -c "from agentx.core.dependencies import get_qdrant_adapter, get_redis_adapter, get_sqlite_adapter, get_ollama_adapter; print('All getters OK')"
```

---

## Implementation Steps

### Step 1: Read existing dependencies.py

First, read the current state of `agentx/core/dependencies.py` (created in T003):

```bash
cat agentx/core/dependencies.py
```

This will show the existing structure that we need to update.

### Step 2: Update dependencies.py with Phase 1 adapters

Replace/update file `agentx/core/dependencies.py`:

```python
"""Dependency injection container for AGENTX.

Following the Mimicus pattern of global singletons with getter functions.
All adapters are lazy-loaded and cached for the application lifetime.
"""

from typing import Optional
from fastapi import FastAPI

from agentx.core.config import Settings, get_settings


# ============================================================================
# Global Singletons (Lazy Initialized)
# ============================================================================

_app: Optional[FastAPI] = None
_settings: Optional[Settings] = None
_qdrant_adapter = None
_redis_adapter = None
_sqlite_adapter = None
_ui_repository = None
_ollama_adapter = None


# ============================================================================
# Application and Settings
# ============================================================================

def get_app() -> FastAPI:
    """Get or create the FastAPI application instance."""
    global _app
    if _app is None:
        from agentx.main import create_app
        _app = create_app()
    return _app


def get_settings() -> Settings:
    """Get or create global Settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


# ============================================================================
# Qdrant Vector Store
# ============================================================================

def get_qdrant_adapter():
    """Get Qdrant vector store adapter instance."""
    global _qdrant_adapter
    if _qdrant_adapter is None:
        from agentx.infrastructure.external.qdrant_vector_store import QdrantVectorStoreAdapter
        from qdrant_client import AsyncQdrantClient

        settings = get_settings()
        client = AsyncQdrantClient(url=settings.qdrant_url)
        _qdrant_adapter = QdrantVectorStoreAdapter(
            client=client,
            collection_name=settings.qdrant_collection_name,
            embedding_dim=settings.qdrant_embedding_dim
        )
    return _qdrant_adapter


# ============================================================================
# Redis Session Storage
# ============================================================================

def get_redis_adapter():
    """Get Redis session adapter instance."""
    global _redis_adapter
    if _redis_adapter is None:
        from agentx.infrastructure.external.redis_session_adapter import RedisSessionAdapter
        from redis import Redis

        settings = get_settings()
        redis_client = Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            decode_responses=True
        )
        _redis_adapter = RedisSessionAdapter(
            redis_client=redis_client,
            ttl_seconds=settings.redis_session_ttl_seconds
        )
    return _redis_adapter


# ============================================================================
# SQLite Session Storage
# ============================================================================

def get_sqlite_adapter():
    """Get SQLite session adapter instance."""
    global _sqlite_adapter
    if _sqlite_adapter is None:
        from agentx.infrastructure.external.sqlite_session_adapter import SQLiteSessionAdapter

        settings = get_settings()
        _sqlite_adapter = SQLiteSessionAdapter(db_path=settings.sqlite_db_path)
    return _sqlite_adapter


# ============================================================================
# Session Repository (with Redis fallback to SQLite)
# ============================================================================

def get_session_repository():
    """Get session repository with Redis → SQLite fallback.

    Returns Redis adapter if available, falls back to SQLite.
    """
    try:
        adapter = get_redis_adapter()
        # Test Redis connection
        adapter.redis.ping()
        return adapter
    except Exception:
        # Fall back to SQLite
        return get_sqlite_adapter()


# ============================================================================
# UI Component Repository (In-Memory)
# ============================================================================

def get_ui_repository():
    """Get in-memory UI component repository instance."""
    global _ui_repository
    if _ui_repository is None:
        from agentx.infrastructure.external.in_memory_ui_repository import InMemoryUIComponentRepository
        _ui_repository = InMemoryUIComponentRepository()
    return _ui_repository


# ============================================================================
# Memory Repository (Qdrant)
# ============================================================================

def get_memory_repository():
    """Get memory repository (Qdrant vector store)."""
    return get_qdrant_adapter()


# ============================================================================
# Ollama LLM Adapter
# ============================================================================

def get_ollama_adapter():
    """Get Ollama LLM adapter instance."""
    global _ollama_adapter
    if _ollama_adapter is None:
        from agentx.infrastructure.external.ollama_llm import OllamaLLMAdapter

        settings = get_settings()
        _ollama_adapter = OllamaLLMAdapter(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
            timeout_seconds=settings.ollama_timeout_seconds
        )
    return _ollama_adapter


# ============================================================================
# Setter Functions (For Testing)
# ============================================================================

def set_app(app: FastAPI) -> None:
    """Override the global app instance (for testing)."""
    global _app
    _app = app


def set_settings(settings: Settings) -> None:
    """Override the global settings instance (for testing)."""
    global _settings
    _settings = settings


def set_qdrant_adapter(adapter) -> None:
    """Override the global Qdrant adapter (for testing)."""
    global _qdrant_adapter
    _qdrant_adapter = adapter


def set_redis_adapter(adapter) -> None:
    """Override the global Redis adapter (for testing)."""
    global _redis_adapter
    _redis_adapter = adapter


def set_sqlite_adapter(adapter) -> None:
    """Override the global SQLite adapter (for testing)."""
    global _sqlite_adapter
    _sqlite_adapter = adapter


def set_ui_repository(repository) -> None:
    """Override the global UI repository (for testing)."""
    global _ui_repository
    _ui_repository = repository


def set_ollama_adapter(adapter) -> None:
    """Override the global Ollama adapter (for testing)."""
    global _ollama_adapter
    _ollama_adapter = adapter


# ============================================================================
# Reset Function (For Testing)
# ============================================================================

def reset_dependencies() -> None:
    """Reset all global singletons (for testing only)."""
    global _app, _settings, _qdrant_adapter, _redis_adapter, _sqlite_adapter, _ui_repository, _ollama_adapter
    _app = None
    _settings = None
    _qdrant_adapter = None
    _redis_adapter = None
    _sqlite_adapter = None
    _ui_repository = None
    _ollama_adapter = None
```

### Step 3: Verify all imports work

Create test script to verify dependencies:

```bash
cat > /tmp/test_dependencies.py << 'EOF'
"""Test dependency injection imports."""
import sys
sys.path.insert(0, "/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R013_travel_planning_stream/backend")

from agentx.core.dependencies import (
    get_settings,
    get_qdrant_adapter,
    get_redis_adapter,
    get_sqlite_adapter,
    get_ui_repository,
    get_ollama_adapter,
    get_session_repository,
    get_memory_repository
)

print("✓ get_settings")
print("✓ get_qdrant_adapter")
print("✓ get_redis_adapter")
print("✓ get_sqlite_adapter")
print("✓ get_ui_repository")
print("✓ get_ollama_adapter")
print("✓ get_session_repository")
print("✓ get_memory_repository")
print("\nAll dependency getters imported successfully!")
EOF

python3 /tmp/test_dependencies.py
```

---

## Expected Failures & Countermeasures

### Failure: Import errors for adapters

**Likelihood**: Low (if T101-T102 complete)
**Symptoms**: `ModuleNotFoundError: No module named 'infrastructure.external.qdrant_vector_store'`

**Countermeasures**:
1. Ensure T101 (Repository Implementations) is complete
2. Ensure T102 (Ollama Adapter) is complete
3. Check all adapter files exist in infrastructure/external/

**Recovery Time**: 5 minutes

### Failure: Redis connection fails on import

**Likelihood**: Medium
**Symptoms**: `redis.exceptions.ConnectionError` when importing dependencies

**Countermeasures**:
1. This is expected - adapters are lazy-loaded
2. Redis connection only happens when get_redis_adapter() is CALLED
3. Import should not fail, only adapter instantiation may fail

**Recovery Time**: 0 minutes (expected behavior)

### Failure: Qdrant client not installed

**Likelihood**: Medium
**Symptoms**: `ModuleNotFoundError: No module named 'qdrant_client'`

**Countermeasures**:
1. Install qdrant-client: `uv pip install qdrant-client`
2. Or stub out Qdrant for Phase 0 testing
3. Add to requirements.txt in T009

**Recovery Time**: 3 minutes

---

## Retroactive Measures

### Upstream Drift Recovery

**Scenario**: T003 dependencies.py changed manually
**Detection**: Existing getter functions missing or renamed
**Action**: This task (T103) replaces T003 version, preserve any custom getters

**Recovery Time**: 5 minutes

**Scenario**: T002 Settings field names changed
**Detection**: AttributeError when accessing settings fields
**Action**: Re-run T002 or update field names in getter functions

**Recovery Time**: 5 minutes

### Downstream Impact

**Scenario**: Getter function signatures change
**Prevention**: All getter function signatures are LOCKED (no parameters)
**Mitigation**: If changes needed, update all use sites
**Affected Tasks**: T200-T299 (Phase 2: Agent Layer), T104 (Tests)

---

## Artifacts

**Files Modified**:
- `agentx/core/dependencies.py` (Complete rewrite with Phase 1 adapters)

**Locked APIs**:
- All getter function names: `get_qdrant_adapter()`, `get_redis_adapter()`, etc.
- All getter function signatures: No parameters, return adapter instances
- All setter function names: `set_qdrant_adapter()`, `set_redis_adapter()`, etc.
- `reset_dependencies()` function

---

## Quality Gates

**Quality Checks**:
- **Check**: dependencies.py exists
  - Command: `test -f agentx/core/dependencies.py && echo "exists"`
  - Expected: `exists`
  - Required: Yes

- **Check**: All getter functions can be imported
  - Command: `python3 -c "from agentx.core.dependencies import get_qdrant_adapter, get_redis_adapter, get_sqlite_adapter, get_ollama_adapter, get_ui_repository; print('OK')"`
  - Expected: `OK`
  - Required: Yes

- **Check**: Settings can be accessed
  - Command: `python3 -c "from agentx.core.dependencies import get_settings; s = get_settings(); print(s.app_name)"`
  - Expected: `AGENTX`
  - Required: Yes

---

## Notes

1. All adapters are singletons (lazy-loaded, cached)
2. Redis → SQLite fallback pattern in get_session_repository()
3. Memory repository aliases to Qdrant adapter
4. Setter functions for testing (override singletons)
5. reset_dependencies() for test cleanup
6. All getter functions follow Mimicus pattern (no parameters)

---

## Completion Checklist

- [ ] dependencies.py updated with all Phase 1 adapters
- [ ] get_qdrant_adapter() implemented
- [ ] get_redis_adapter() implemented
- [ ] get_sqlite_adapter() implemented
- [ ] get_ui_repository() implemented
- [ ] get_ollama_adapter() implemented
- [ ] get_session_repository() with fallback
- [ ] get_memory_repository() (alias to Qdrant)
- [ ] All setter functions implemented
- [ ] reset_dependencies() implemented
- [ ] All imports work
- [ ] Ready for T104 (Phase 1 Tests)

---

**Task T103 is part of Phase 1: Domain + Infrastructure**
**Locked APIs**: All getter/setter function signatures
