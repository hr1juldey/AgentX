# AGENTX Task Template

**Version**: 1.0.0
**Date**: 2026-01-19
**Part of**: AGENTX Task Management System

---

## Purpose

This template defines the structure for all AGENTX tasks. Each task should be:
- **Small enough** to complete in one Ralph Loop session (30-60 min)
- **Self-contained** with all necessary context
- **Verifiable** with clear passing criteria
- **Resilient** with expected failures and countermeasures
- **Recoverable** with retroactive measures for drift

---

## Template Structure

```yaml
# ============================================================================
# TASK METADATA
# ============================================================================
task_id: "TXXX"
task_name: "Brief human-readable name"
phase: "X"  # 0-7 from incremental_release_plan.md
estimated_minutes: 30-60
dependencies: ["TXXX", "TYYY"]  # Prerequisite task IDs
blocked_by: []  # Optional: tasks that block this one

# ============================================================================
# CONTEXT
# ============================================================================
lld_references:
  - "LLD.md section: X.Y"
  - "lld/domain_model.md section: Entities"

description: |
  What this task does and why it matters.
  Connect to the bigger picture.

# ============================================================================
# ACCEPTANCE CRITERIA
# ============================================================================
passing_criteria:
  - criterion_1: "Specific, measurable outcome"
  - criterion_2: "Another specific outcome"
  - files_created: "List of files that must exist"
  - files_modified: "List of files that must be modified"

verification_commands:
  - command: "bash command to verify"
    expected_output: "Expected result"

# ============================================================================
# IMPLEMENTATION STEPS
# ============================================================================
steps:
  - step_number: 1
    description: "Brief description"
    action: |
      Detailed instructions for this step.
      Include code snippets if applicable.

  - step_number: 2
    description: "Brief description"
    action: |
      Detailed instructions for this step.

# ============================================================================
# EXPECTED FAILURES & COUNTERMEASURES
# ============================================================================
expected_failures:
  - failure: "Name of potential failure"
    likelihood: "high/medium/low"
    symptoms: "How to recognize this failure"
    countermeasures:
      - "Specific action to take"
      - "Alternative action if first doesn't work"
    recovery_time_minutes: 5

# ============================================================================
# RETROACTIVE MEASURES
# ============================================================================
# What to do if upstream tasks changed or downstream tasks break
upstream_drift_recovery:
  - scenario: "Upstream task X changed file Y"
    detection: "How to detect this happened"
    action: "What to do to realign"
    estimated_recovery_minutes: 15

downstream_impact:
  - scenario: "This task breaks downstream task Y"
    prevention: "How to prevent breaking downstream"
    mitigation: "How to fix if breakage occurs"
    affected_tasks: ["TYYY", "TZZZ"]

# ============================================================================
# ARTIFACTS
# ============================================================================
files_created:
  - path: "relative/path/to/file.ext"
    purpose: "What this file does"
    locked: true  # If API is now frozen

  - path: "relative/path/to/another.ext"
    purpose: "What this file does"
    locked: false

files_modified:
  - path: "relative/path/to/file.ext"
    changes: "Summary of changes made"
    locked: false

# ============================================================================
# QUALITY GATES
# ============================================================================
quality_checks:
  - check: "Ruff lint passes"
    command: "ruff check agentx/"
    required: true

  - check: "Ruff format passes"
    command: "ruff format agentx/"
    required: true

  - check: "Pyrefly type check passes"
    command: "pyrefly check agentx/ --summarize-errors"
    required: true

  - check: "Tests pass"
    command: "pytest tests/unit/path/to/test_file.py"
    required: true

# ============================================================================
# NOTES
# ============================================================================
notes: |
  Any additional context, warnings, or special considerations
  for the person/AI executing this task.
```

---

## Field Definitions

### Task Metadata

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `task_id` | string | Yes | Unique identifier (T000-T999) |
| `task_name` | string | Yes | Human-readable name |
| `phase` | int | Yes | Which phase (0-7) this belongs to |
| `estimated_minutes` | int | Yes | Time to complete (30-120 min) |
| `dependencies` | list | Yes | Prerequisite task IDs |
| `blocked_by` | list | No | Tasks that block this one |

### Acceptance Criteria

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `passing_criteria` | list | Yes | Specific, measurable outcomes |
| `verification_commands` | list | Yes | Commands to verify success |

### Implementation Steps

Each step must have:
- `step_number`: Sequential integer
- `description`: One-line summary
- `action`: Detailed instructions (can include code)

### Expected Failures

For each potential failure:
- `failure`: Name/description
- `likelihood`: high/medium/low
- `symptoms`: How to recognize
- `countermeasures`: Actions to take (ordered list)
- `recovery_time_minutes`: Estimated time to recover

### Retroactive Measures

**Upstream Drift Recovery**: What if prerequisite tasks changed?
- `scenario`: What changed
- `detection`: How to detect
- `action`: How to realign

**Downstream Impact**: What if this breaks future tasks?
- `scenario`: What might break
- `prevention`: How to prevent
- `mitigation`: How to fix
- `affected_tasks`: List of task IDs

### Artifacts

**Files Created**:
- `path`: Relative to project root
- `purpose`: What the file does
- `locked`: Is the API now frozen (no changes allowed)?

**Files Modified**:
- `path`: Relative to project root
- `changes`: Summary of changes

### Quality Gates

Each quality check must have:
- `check`: Description
- `command`: Exact command to run
- `required`: Can task complete if this fails?

---

## Task ID Assignment

- **T000-T099**: Phase 0 tasks
- **T100-T199**: Phase 1 tasks
- **T200-T299**: Phase 2 tasks
- **T300-T399**: Phase 3 tasks
- **T400-T499**: Phase 4 tasks
- **T500-T599**: Phase 5 tasks
- **T600-T699**: Phase 6 tasks
- **T700-T799**: Phase 7 tasks

---

## Execution Guidelines for Ralph Loop

### Before Starting

1. **Check dependencies**: Ensure all prerequisite tasks are complete
2. **Read LLD references**: Review linked LLD sections
3. **Verify starting state**: Run verification commands to see current state

### During Execution

1. **Follow steps sequentially**: Don't skip ahead
2. **Document deviations**: If you deviate from steps, note why
3. **Handle failures**: Use countermeasures from template
4. **Run quality gates**: After each step, run relevant quality checks

### After Completion

1. **Run all verification commands**: Confirm passing criteria met
2. **Update task status**: Mark task as complete
3. **Check downstream impact**: Verify dependent tasks can proceed
4. **Create checkpoint**: Commit changes with task ID in message

### On Failure

1. **Identify failure type**: Match against expected failures
2. **Apply countermeasures**: Try each countermeasure in order
3. **Document actual failure**: Add to task notes if new failure type
4. **Recover or rollback**: Use retroactive measures if needed

### Context Wipeout Recovery

If context is lost during execution:
1. **Find last checkpoint**: Look for task ID in git commits
2. **Identify current task**: Check which tasks are complete
3. **Resume from current task**: Re-read task and continue
4. **No drift possible**: Task is self-contained with all context

---

## Example Task

See `tasks/phase_0/T000_example.md` for a complete example.

---

**This template is part of AGENTX Task Management System v1.0.**
