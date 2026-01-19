# T002: Create Pydantic Settings

**Phase**: 0
**Estimated Time**: 20 minutes
**Dependencies**: T001
**Blocked By**: None

---

## Context

**LLD References**:
- `lld/infrastructure_adapters.md` - QdrantAdapter, OllamaLLMAdapter config patterns
- `lld/incremental_release_plan.md` - Phase 0: Settings structure frozen

**Description**:
Creates Pydantic Settings class for configuration management with .env file support. Settings structure is now **frozen** - changes require new major version.

---

## Acceptance Criteria

**Passing Criteria**:
- `core/config.py` exists with Settings class
- Settings class has all required fields (app_name, version, port, etc.)
- Settings loads from .env file
- Settings validates on startup
- .env.example template exists

**Verification Commands**:
```bash
cd /home/riju279/Documents/Code/XRIG/AgentX/prototypes/R013_travel_planning_stream/backend

# Verify file exists
test -f agentx/core/config.py && echo "config.py exists"

# Verify Settings can be imported
python3 -c "from agentx.core.config import Settings; print('Import successful')"

# Verify .env.example exists
test -f agentx/.env.example && echo ".env.example exists"
```

---

## Implementation Steps

### Step 1: Create Settings class

Create file `agentx/core/config.py`:

```python
"""Configuration management with Pydantic Settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseModel):
    """Application configuration loaded from environment variables.

    All fields are documented with descriptions.
    Default values are provided for development.
    """

    # Application Info
    app_name: str = "AGENTX"
    version: str = "1.0.0"
    environment: str = "development"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    reload: bool = True

    # LLM Configuration (Ollama)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "gemma3:4b"
    ollama_timeout_seconds: int = 120

    # DSPy Configuration
    dspy_max_iters: int = 8
    dspy_confidence_threshold: float = 0.7

    # Qdrant Vector Store
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection_name: str = "agentx_memories"
    qdrant_embedding_dim: int = 384

    # Redis (Session Storage)
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_session_ttl_seconds: int = 3600

    # SQLite (Long-term Storage)
    sqlite_db_path: str = "data/sessions.db"

    # Mem0AI (Long-term Memory)
    mem0_enabled: bool = False
    mem0_api_key: Optional[str] = None

    # WebSocket
    websocket_ping_interval_seconds: int = 20
    websocket_ping_timeout_seconds: int = 30

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"  # "json" or "text"

    # Security
    secret_key: str = "change-this-in-production"
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # File Storage
    data_dir: str = "data"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra env vars
```

### Step 2: Create settings getter function

Add to `agentx/core/config.py` (at end):

```python
# Global settings instance (lazy loaded)
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create global Settings instance.

    Returns:
        Settings: The application settings singleton

    Example:
        >>> settings = get_settings()
        >>> print(settings.app_name)
        AGENTX
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
```

### Step 3: Create .env.example

Create file `agentx/.env.example`:

```bash
# ============================================================================
# AGENTX Environment Configuration
# ============================================================================
# Copy this file to .env and update with your values

# Application
APP_NAME=AGENTX
VERSION=1.0.0
ENVIRONMENT=development

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=true
RELOAD=true

# LLM (Ollama)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma3:4b
OLLAMA_TIMEOUT_SECONDS=120

# DSPy
DSPY_MAX_ITERS=8
DSPY_CONFIDENCE_THRESHOLD=0.7

# Qdrant Vector Store
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION_NAME=agentx_memories
QDRANT_EMBEDDING_DIM=384

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_SESSION_TTL_SECONDS=3600

# SQLite
SQLITE_DB_PATH=data/sessions.db

# Mem0AI
MEM0_ENABLED=false
# MEM0_API_KEY=your-api-key-here

# WebSocket
WEBSOCKET_PING_INTERVAL_SECONDS=20
WEBSOCKET_PING_TIMEOUT_SECONDS=30

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Security
SECRET_KEY=change-this-in-production-use-openssl-rand-hex-32
CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]

# File Storage
DATA_DIR=data
```

### Step 4: Create empty .env file

```bash
cd /home/riju279/Documents/Code/XRIG/AgentX/prototypes/R013_travel_planning_stream/backend/agentx

# Create empty .env file
touch .env

# Add to .gitignore (if not already there)
echo ".env" >> .gitignore
```

---

## Expected Failures & Countermeasures

### Failure: ImportError for pydantic_settings

**Likelihood**: Medium
**Symptoms**: `ModuleNotFoundError: No module named 'pydantic_settings'`

**Countermeasures**:
1. Install pydantic-settings: `uv add pydantic-settings`
2. If uv not available, use pip: `pip install pydantic-settings`
3. Check requirements-core.txt includes pydantic-settings

**Recovery Time**: 3 minutes

### Failure: ValidationError on startup

**Likelihood**: Low
**Symptoms**: `pydantic_core._pydantic_core.ValidationError: ...`

**Countermeasures**:
1. Check .env file has valid values (strings quoted for list)
2. Check numeric fields are valid numbers
3. Check boolean fields are "true"/"false" (lowercase)
4. Run validation: `python3 -c "from agentx.core.config import Settings; Settings()"`

**Recovery Time**: 5 minutes

### Failure: .env file not found

**Likelihood**: Low (Pydantic uses defaults if missing)
**Symptoms**: Warning message about missing .env

**Countermeasures**:
1. Copy .env.example to .env: `cp .env.example .env`
2. Update .env with actual values

**Recovery Time**: 2 minutes

---

## Retroactive Measures

### Upstream Drift Recovery

**Scenario**: T001 directory structure changed
**Detection**: `agentx/core/` directory doesn't exist
**Action**: Re-run T001 to ensure all directories exist

**Recovery Time**: 5 minutes

### Downstream Impact

**Scenario**: Settings fields change or are renamed
**Prevention**: Settings structure is now FROZEN per LLD
**Mitigation**: If changes absolutely required, must update all dependent tasks
**Affected Tasks**: T003 (DI), T004 (CORS), T005 (Logging), T006 (App Factory)

---

## Artifacts

**Files Created**:
- `agentx/core/config.py` (Settings class, LOCKED - Phase 0 API)
- `agentx/.env.example` (Environment template, not locked)
- `agentx/.env` (Local environment, not in git)
- `agentx/.gitignore` entry for .env

**Files Modified**:
- `.gitignore` (add .env entry)

**Locked APIs**:
- `Settings` class name and all field names
- `get_settings()` function signature
- .env field names (must match Settings fields)

---

## Quality Gates

**Quality Checks**:
- **Check**: Settings can be imported
  - Command: `python3 -c "from agentx.core.config import get_settings; s = get_settings(); print(s.app_name)"`
  - Expected: `AGENTX`
  - Required: Yes

- **Check**: Settings validates
  - Command: `python3 -c "from agentx.core.config import Settings; Settings(port=-1)"` 2>&1 | grep -i error
  - Expected: Validation error for invalid port
  - Required: Yes

- **Check**: .env.example exists
  - Command: `test -f agentx/.env.example && echo "Exists"`
  - Expected: `Exists`
  - Required: Yes

---

## Notes

1. Settings fields are **frozen** after this task - no breaking changes allowed
2. Use `get_settings()` function, don't instantiate Settings directly
3. .env file should never be committed to git
4. .env.example should document all possible fields
5. Boolean values in .env must be lowercase "true"/"false"
6. List values in .env must be JSON format: `['http://localhost']`

---

## Completion Checklist

- [ ] agentx/core/config.py created with Settings class
- [ ] get_settings() function implemented
- [ ] .env.example created with all fields documented
- [ ] .env file created (empty or with defaults)
- [ ] .gitignore updated with .env entry
- [ ] Import test passes
- [ ] Validation test passes
- [ ] Ready for T003 (Dependency Injection)

---

**Task T002 is part of Phase 0: Minimal System**
**Locked API**: Settings class fields and get_settings() signature
