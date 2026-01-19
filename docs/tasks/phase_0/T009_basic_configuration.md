# T009: Create Basic Configuration Files

**Phase**: 0
**Estimated Time**: 15 minutes
**Dependencies**: T002
**Blocked By**: None

---

## Context

**LLD References**:
- `lld/incremental_release_plan.md` - Phase 0: Configuration files

**Description**:
Creates configuration files for the project: .env.example, pyproject.toml, requirements.txt, .gitignore, and basic README. These files are used by all subsequent tasks.

---

## Acceptance Criteria

**Passing Criteria**:
- .env.example exists with all documented fields
- .gitignore exists with proper exclusions
- pyproject.toml exists (or placeholder)
- requirements.txt exists with core dependencies
- README.md exists with project info

**Verification Commands**:
```bash
cd /home/riju279/Documents/Code/XRIG/AgentX/prototypes/R013_travel_planning_stream/backend/agentx

# Verify files exist
test -f .env.example && echo ".env.example exists"
test -f .gitignore && echo ".gitignore exists"
test -f pyproject.toml && echo "pyproject.toml exists"
test -f requirements.txt && echo "requirements.txt exists"
test -f README.md && echo "README.md exists"
```

---

## Implementation Steps

### Step 1: Create .gitignore

Create file `agentx/.gitignore`:

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
.venv/
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Environment
.env
.env.local
.env.*.local

# Data
data/
*.db
*.sqlite
*.sqlite3

# Logs
logs/
*.log

# OS
.DS_Store
Thumbs.db

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/
.hypothesis/

# Jupyter
.ipynb_checkpoints/
*.ipynb

# MyPy
.mypy_cache/
.dmypy.json
dmypy.json

# Ruff
.ruff_cache/
```

### Step 2: Update .env.example

Update `agentx/.env.example` (created in T002, verify and enhance):

```bash
cd /home/riju279/Documents/Code/XRIG/AgentX/prototypes/R013_travel_planning_stream/backend/agentx

cat > .env.example << 'EOF'
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
EOF
```

### Step 3: Create requirements.txt

Create file `agentx/requirements.txt`:

```txt
# ============================================================================
# AGENTX Dependencies
# ============================================================================

# FastAPI and Web
fastapi==0.104.1
uvicorn[standard]==0.24.0
websockets==12.0

# Pydantic and Validation
pydantic==2.5.0
pydantic-settings==2.1.0

# DSPy
dspy-ai==2.5.0

# Database and Storage
qdrant-client==1.7.0
redis==5.0.1

# HTTP Client
aiohttp==3.9.1
httpx==0.25.2

# Async Support
async-timeout==4.0.3

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0

# Code Quality
ruff==0.1.9

# Type Checking (optional)
pyrefly==0.1.1

# Logging
python-json-logger==2.0.7

# Utilities
python-dotenv==1.0.0
```

### Step 4: Create pyproject.toml

Create file `agentx/pyproject.toml`:

```toml
[project]
name = "agentx"
version = "1.0.0"
description = "Local-first AI personal assistant with temporal memory and voice interface"
readme = "README.md"
requires-python = ">=3.9"
dependencies = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.1.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
line-length = 100
target-version = "py39"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "B"]
ignore = ["E501"]  # Line too long (handled by formatter)

[tool.ruff.format]
quote-style = "double"
indent-style = "space"

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

### Step 5: Update README.md

Update `agentx/README.md` (created in T001):

```bash
cat > README.md << 'EOF'
# AGENTX

Local-first AI personal assistant with temporal memory, voice interface, and extensible plugins.

## Quick Start

```bash
# Install dependencies
uv pip install -r requirements.txt

# Start Ollama (required)
ollama serve
ollama pull gemma3:4b

# Start AGENTX
python -m agentx.main
```

## Architecture

Clean Architecture / DDD with:
- **Domain Layer**: Entities, repositories, services
- **Application Layer**: Use cases, DTOs, mappers
- **Infrastructure Layer**: External adapters (DB, APIs)
- **Agent Layer**: DSPy agents, LangGraph state machines
- **UI Layer**: Descriptors and WebSocket protocols
- **Plugin Layer**: Extensible plugin system

## Documentation

- [LLD](../engineering/LLD.md) - Low-Level Design
- [HLD](../engineering/HLD.md) - High-Level Design
- [Task List](../tasks/) - Incremental implementation tasks

## Status

**Phase 0**: Minimal System (In Progress)

Phase 0 creates the basic FastAPI server with configuration, middleware, and stub repositories.

## Development

```bash
# Install dependencies
uv pip install -r requirements.txt

# Run with auto-reload
python -m agentx.main

# Run tests
pytest

# Lint
ruff check .
ruff format .

# Type check
pyrefly check . --summarize-errors
```

## License

MIT

---

**Part of AGENTX v1.0 - See [../engineering/LLD.md](../engineering/LLD.md)**
EOF
```

---

## Expected Failures & Countermeasures

### Failure: uv command not found

**Likelihood**: Medium
**Symptoms**: `bash: uv: command not found`

**Countermeasures**:
1. Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
2. Or use pip instead of uv
3. Update documentation to use pip if uv unavailable

**Recovery Time**: 5 minutes

---

## Retroactive Measures

### Upstream Drift Recovery

**Scenario**: T002 .env.example changed
**Detection**: .env.example out of sync
**Action**: Copy T002 version or merge changes

**Recovery Time**: 3 minutes

### Downstream Impact

**Scenario**: requirements.txt missing dependencies
**Prevention**: Keep requirements.txt updated with all used packages
**Mitigation**: Run `uv pip freeze > requirements.txt` to capture current state
**Affected Tasks**: All subsequent tasks requiring dependencies

---

## Artifacts

**Files Created**:
- `agentx/.gitignore` (Git ignore rules, not locked)
- `agentx/requirements.txt` (Dependencies, not locked)
- `agentx/pyproject.toml` (Project config, not locked)
- `agentx/README.md` (Documentation, not locked)

**Files Modified**:
- `agentx/.env.example` (Verified complete, not locked)

---

## Quality Gates

**Quality Checks**:
- **Check**: All files exist
  - Command: `ls .gitignore .env.example requirements.txt pyproject.toml README.md`
  - Expected: All files listed
  - Required: Yes

- **Check**: .env.example is complete
  - Command: `grep -c "=" .env.example`
  - Expected: > 20 (has many config fields)
  - Required: Yes

---

## Notes

1. requirements.txt should be updated as dependencies are added
2. .env.example should document ALL possible env vars
3. .gitignore ensures .env is never committed
4. pyproject.toml configures ruff and pytest
5. README.md provides quick start for developers

---

## Completion Checklist

- [ ] .gitignore created with proper exclusions
- [ ] .env.example verified complete
- [ ] requirements.txt created with core dependencies
- [ ] pyproject.toml created with ruff config
- [ ] README.md updated with quick start
- [ ] All verification commands pass
- [ ] Phase 0 complete!

---

## Phase 0 Summary

**Tasks Completed**:
- T001: Directory structure
- T002: Pydantic Settings
- T003: Dependency Injection
- T004: CORS Middleware
- T005: Logging Middleware
- T006: FastAPI Application Factory
- T007: Health Endpoint
- T008: Stub Repositories
- T009: Configuration Files

**Phase 0 Deliverables**:
- FastAPI server that starts without errors
- Health endpoint at `/health`
- Configuration management with .env
- Clean Architecture file structure
- Middleware (CORS, logging) configured
- Repository interfaces defined (stub implementations)

**Next Phase**: Phase 1 - Domain + Infrastructure (2-3 hours)

---

**Task T009 is part of Phase 0: Minimal System**
**Phase 0 Status**: ✅ COMPLETE
