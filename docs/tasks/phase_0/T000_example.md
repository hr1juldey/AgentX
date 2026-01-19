# T000: Example Task - Create Project Directory Structure

**Phase**: 0
**Estimated Time**: 15 minutes
**Dependencies**: None
**Blocked By**: None

---

## Context

**LLD References**:
- `LLD.md` - File Structure Reference section

**Description**:
This task creates the basic directory structure for the AGENTX project following Clean Architecture principles. All subsequent tasks depend on this structure existing.

---

## Acceptance Criteria

**Passing Criteria**:
- All required directories exist
- Each directory contains an `__init__.py` file (except tests/)
- Directory structure matches LLD.md specification exactly

**Verification Commands**:
```bash
# Verify directories exist
ls -la agentx/core/
ls -la agentx/domain/
ls -la agentx/application/
ls -la agentx/infrastructure/
ls -la agentx/agent/
ls -la agentx/ui/
ls -la agentx/plugin/
ls -la agentx/presentation/
ls -la agentx/tests/

# Verify __init__.py files exist
find agentx -name "__init__.py" | grep -v __pycache__
```

---

## Implementation Steps

### Step 1: Create root directories

```bash
cd /home/riju279/Documents/Code/XRIG/AgentX/prototypes/R013_travel_planning_stream/backend

# Create main package directory
mkdir -p agentx
cd agentx
```

### Step 2: Create layer directories

```bash
# Core layer
mkdir -p core/middleware

# Domain layer
mkdir -p domain/entities
mkdir -p domain/repositories
mkdir -p domain/services

# Application layer
mkdir -p application/use_cases
mkdir -p application/commands
mkdir -p application/queries
mkdir -p application/dtos
mkdir -p application/mappers

# Infrastructure layer
mkdir -p infrastructure/database
mkdir -p infrastructure/external

# Agent layer
mkdir -p agent/dspy_signatures
mkdir -p agent/tools
mkdir -p agent/dspy_agents
mkdir -p agent/langgraph

# UI layer
mkdir -p ui/descriptors
mkdir -p ui/protocols

# Plugin layer
mkdir -p plugin

# Presentation layer
mkdir -p presentation/api/v1

# Tests
mkdir -p tests/unit/domain
mkdir -p tests/unit/application
mkdir -p tests/unit/infrastructure
mkdir -p tests/integration/agent
mkdir -p tests/integration/infrastructure
mkdir -p tests/e2e
```

### Step 3: Create __init__.py files

```bash
# Create __init__.py for all Python packages
find agentx -type d -exec touch {}/__init__.py \;

# Remove __init__.py from tests/ (tests don't need it)
rm tests/__init__.py
find tests -type d -exec rm -f {}/__init__.py \;
```

### Step 4: Create placeholder README

```bash
cat > agentx/README.md << 'EOF'
# AGENTX

Local-first AI personal assistant with temporal memory, voice interface, and extensible plugins.

## Status

Under active development.

## Documentation

See `docs/engineering/LLD.md` for complete Low-Level Design.
EOF
```

---

## Expected Failures & Countermeasures

### Failure: Directory already exists

**Likelihood**: High
**Symptoms**: `mkdir: cannot create directory 'agentx': File exists`

**Countermeasures**:
1. If directory is empty, continue with structure
2. If directory has content, back up and start fresh
3. If directory is from previous attempt, verify structure matches LLD

**Recovery Time**: 2 minutes

### Failure: Permission denied

**Likelihood**: Low
**Symptoms**: `mkdir: cannot create directory: Permission denied`

**Countermeasures**:
1. Check directory ownership: `ls -la`
2. Ensure write permissions on parent directory
3. Use `sudo` only if absolutely necessary (not recommended)

**Recovery Time**: 5 minutes

---

## Retroactive Measures

### Upstream Drift Recovery

**Scenario**: Previous tasks modified directory structure
**Detection**: Directories don't match LLD.md specification
**Action**:
1. Compare current structure with LLD.md
2. Add missing directories
3. Remove extra directories (after backing up)
4. Verify all `__init__.py` files exist

**Recovery Time**: 10 minutes

### Downstream Impact

**Scenario**: Directory names don't match what other tasks expect
**Prevention**: Follow LLD.md exactly, use exact spelling
**Mitigation**: If names are wrong, this task must be redone
**Affected Tasks**: All Phase 0 tasks (T001-T009)

---

## Artifacts

**Files Created**:
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
- `agentx/README.md` (Documentation, not locked)

**Files Modified**: None

---

## Quality Gates

**Quality Checks**:
- **Check**: Directory structure matches LLD.md
  - Command: `tree agentx -L 2`
  - Required: Yes

- **Check**: All Python packages have __init__.py
  - Command: `find agentx -type d -name "__init__.py" | grep -v __pycache__ | wc -l`
  - Expected: 28 (all packages except tests/)
  - Required: Yes

---

## Notes

1. This task is idempotent - running it multiple times is safe
2. The `tests/` directory does NOT get `__init__.py` files (pytest convention)
3. All directory names must match LLD.md exactly (case-sensitive)
4. Use absolute paths or ensure you're in the correct directory before running commands
5. If running in a different directory, update all paths in this task

---

## Completion Checklist

- [ ] All directories created
- [ ] All `__init__.py` files created (except tests/)
- [ ] README.md created
- [ ] Directory structure verified against LLD.md
- [ ] No permission errors
- [ ] Ready for next task (T001)

---

**This task is part of Phase 0: Minimal System (2-3 hours total)**
