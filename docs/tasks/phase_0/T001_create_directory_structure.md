# T001: Create Project Directory Structure

**Phase**: 0
**Estimated Time**: 15 minutes
**Dependencies**: None
**Blocked By**: None

---

## Context

**LLD References**:
- `LLD.md` - File Structure Reference section
- `lld/incremental_release_plan.md` - Phase 0: Minimal System

**Description**:
Creates the basic directory structure for the AGENTX project following Clean Architecture principles. This is the foundation for all subsequent tasks.

---

## Acceptance Criteria

**Passing Criteria**:
- All required directories exist under `agentx/`
- Each Python package has an `__init__.py` file
- Tests directory exists but has NO `__init__.py` files
- Structure exactly matches LLD.md specification

**Verification Commands**:
```bash
# From backend directory
cd /home/riju279/Documents/Code/XRIG/AgentX/prototypes/R013_travel_planning_stream/backend

# Verify all directories exist
ls -d agentx/core agentx/core/middleware
ls -d agentx/domain agentx/domain/entities agentx/domain/repositories agentx/domain/services
ls -d agentx/application agentx/application/use_cases agentx/application/commands agentx/application/queries agentx/application/dtos agentx/application/mappers
ls -d agentx/infrastructure agentx/infrastructure/database agentx/infrastructure/external
ls -d agentx/agent agentx/agent/dspy_signatures agentx/agent/tools agentx/agent/dspy_agents agentx/agent/langgraph
ls -d agentx/ui agentx/ui/descriptors agentx/ui/protocols
ls -d agentx/plugin
ls -d agentx/presentation agentx/presentation/api agentx/presentation/api/v1
ls -d tests/unit tests/unit/domain tests/unit/application tests/unit/infrastructure
ls -d tests/integration tests/integration/agent tests/integration/infrastructure
ls -d tests/e2e

# Verify __init__.py files (should be 28)
find agentx -name "__init__.py" | grep -v __pycache__ | wc -l

# Verify tests/ has no __init__.py
find tests -name "__init__.py" | wc -l
```

---

## Implementation Steps

### Step 1: Create all directories

```bash
cd /home/riju279/Documents/Code/XRIG/AgentX/prototypes/R013_travel_planning_stream/backend

# Create root package
mkdir -p agentx

# Core layer
mkdir -p agentx/core/middleware

# Domain layer
mkdir -p agentx/domain/entities
mkdir -p agentx/domain/repositories
mkdir -p agentx/domain/services

# Application layer
mkdir -p agentx/application/use_cases
mkdir -p agentx/application/commands
mkdir -p agentx/application/queries
mkdir -p agentx/application/dtos
mkdir -p agentx/application/mappers

# Infrastructure layer
mkdir -p agentx/infrastructure/database
mkdir -p agentx/infrastructure/external

# Agent layer
mkdir -p agentx/agent/dspy_signatures
mkdir -p agentx/agent/tools
mkdir -p agentx/agent/dspy_agents
mkdir -p agentx/agent/langgraph

# UI layer
mkdir -p agentx/ui/descriptors
mkdir -p agentx/ui/protocols

# Plugin layer
mkdir -p agentx/plugin

# Presentation layer
mkdir -p agentx/presentation/api/v1

# Tests (no __init__.py)
mkdir -p tests/unit/domain
mkdir -p tests/unit/application
mkdir -p tests/unit/infrastructure
mkdir -p tests/integration/agent
mkdir -p tests/integration/infrastructure
mkdir -p tests/e2e
```

### Step 2: Create __init__.py files

```bash
# Create __init__.py for all Python packages (NOT tests/)
touch agentx/__init__.py
touch agentx/core/__init__.py
touch agentx/core/middleware/__init__.py
touch agentx/domain/__init__.py
touch agentx/domain/entities/__init__.py
touch agentx/domain/repositories/__init__.py
touch agentx/domain/services/__init__.py
touch agentx/application/__init__.py
touch agentx/application/use_cases/__init__.py
touch agentx/application/commands/__init__.py
touch agentx/application/queries/__init__.py
touch agentx/application/dtos/__init__.py
touch agentx/application/mappers/__init__.py
touch agentx/infrastructure/__init__.py
touch agentx/infrastructure/database/__init__.py
touch agentx/infrastructure/external/__init__.py
touch agentx/agent/__init__.py
touch agentx/agent/dspy_signatures/__init__.py
touch agentx/agent/tools/__init__.py
touch agentx/agent/dspy_agents/__init__.py
touch agentx/agent/langgraph/__init__.py
touch agentx/ui/__init__.py
touch agentx/ui/descriptors/__init__.py
touch agentx/ui/protocols/__init__.py
touch agentx/plugin/__init__.py
touch agentx/presentation/__init__.py
touch agentx/presentation/api/__init__.py
touch agentx/presentation/api/v1/__init__.py
```

### Step 3: Create README

```bash
cat > agentx/README.md << 'EOF'
# AGENTX

Local-first AI personal assistant with temporal memory, voice interface, and extensible plugins.

## Architecture

Clean Architecture / DDD with:
- **Domain Layer**: Entities, repositories, services
- **Application Layer**: Use cases, DTOs, mappers
- **Infrastructure Layer**: External adapters (DB, APIs)
- **Agent Layer**: DSPy agents, LangGraph state machines
- **UI Layer**: Descriptors and WebSocket protocols
- **Plugin Layer**: Extensible plugin system

## Documentation

See `docs/engineering/LLD.md` for complete Low-Level Design.

## Status

Phase 0: Minimal System (In Progress)
EOF
```

---

## Expected Failures & Countermeasures

### Failure: Directory already exists

**Likelihood**: High
**Symptoms**: `mkdir: cannot create directory 'File exists'`

**Countermeasures**:
1. Check if directory is from previous attempt: `ls -la agentx/`
2. If structure matches LLD.md, continue to next step
3. If structure differs, backup and remove: `mv agentx agentx.backup`
4. Re-run directory creation commands

**Recovery Time**: 5 minutes

### Failure: Permission denied

**Likelihood**: Low
**Symptoms**: `mkdir: cannot create directory: Permission denied`

**Countermeasures**:
1. Check parent directory permissions: `ls -la .`
2. Ensure user owns parent directory or has write access
3. Do NOT use sudo (creates ownership issues)

**Recovery Time**: 2 minutes

---

## Retroactive Measures

### Upstream Drift Recovery

**Scenario**: None (this is the first task)

### Downstream Impact

**Scenario**: Directory names don't match what other tasks expect
**Prevention**: Use exact names from LLD.md (case-sensitive, underscores not hyphens)
**Mitigation**: If wrong, this task must be redone before proceeding
**Affected Tasks**: All Phase 0 tasks (T002-T009)

---

## Artifacts

**Files Created**:
- `agentx/` (Root package, not locked)
- `agentx/README.md` (Documentation, not locked)
- `agentx/__init__.py` (Package marker, not locked)
- `agentx/core/__init__.py` (Package marker, not locked)
- `agentx/core/middleware/__init__.py` (Package marker, not locked)
- `agentx/domain/__init__.py` (Package marker, not locked)
- `agentx/domain/entities/__init__.py` (Package marker, not locked)
- `agentx/domain/repositories/__init__.py` (Package marker, not locked)
- `agentx/domain/services/__init__.py` (Package marker, not locked)
- `agentx/application/__init__.py` (Package marker, not locked)
- `agentx/application/use_cases/__init__.py` (Package marker, not locked)
- `agentx/application/commands/__init__.py` (Package marker, not locked)
- `agentx/application/queries/__init__.py` (Package marker, not locked)
- `agentx/application/dtos/__init__.py` (Package marker, not locked)
- `agentx/application/mappers/__init__.py` (Package marker, not locked)
- `agentx/infrastructure/__init__.py` (Package marker, not locked)
- `agentx/infrastructure/database/__init__.py` (Package marker, not locked)
- `agentx/infrastructure/external/__init__.py` (Package marker, not locked)
- `agentx/agent/__init__.py` (Package marker, not locked)
- `agentx/agent/dspy_signatures/__init__.py` (Package marker, not locked)
- `agentx/agent/tools/__init__.py` (Package marker, not locked)
- `agentx/agent/dspy_agents/__init__.py` (Package marker, not locked)
- `agentx/agent/langgraph/__init__.py` (Package marker, not locked)
- `agentx/ui/__init__.py` (Package marker, not locked)
- `agentx/ui/descriptors/__init__.py` (Package marker, not locked)
- `agentx/ui/protocols/__init__.py` (Package marker, not locked)
- `agentx/plugin/__init__.py` (Package marker, not locked)
- `agentx/presentation/__init__.py` (Package marker, not locked)
- `agentx/presentation/api/__init__.py` (Package marker, not locked)
- `agentx/presentation/api/v1/__init__.py` (Package marker, not locked)
- `tests/` directory tree (No __init__.py, pytest convention)

---

## Quality Gates

**Quality Checks**:
- **Check**: Correct number of __init__.py files
  - Command: `find agentx -name "__init__.py" | grep -v __pycache__ | wc -l`
  - Expected: 28
  - Required: Yes

- **Check**: Tests directory has no __init__.py
  - Command: `find tests -name "__init__.py" | wc -l`
  - Expected: 0
  - Required: Yes

---

## Notes

1. Directory names are case-sensitive
2. Use underscores, not hyphens (Python convention)
3. Tests directory does NOT get __init__.py files
4. All paths in this task assume starting from `R013_travel_planning_stream/backend/`
5. This task is idempotent - can be re-run if needed

---

## Completion Checklist

- [ ] All directories created
- [ ] All __init__.py files created (28 total)
- [ ] Tests/ has no __init__.py files
- [ ] README.md created
- [ ] Verification commands pass
- [ ] Ready for T002 (Pydantic Settings)

---

**Task T001 is part of Phase 0: Minimal System**
