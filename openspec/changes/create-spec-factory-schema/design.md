## Context

**Background**: AgentX v0.1 requires locking down 6 major specification areas (folder structure, data contracts, agent pipeline, voice streaming, memory RAG, release plan). Manual specification of 200+ files across R000-R014 prototypes is infeasible.

**Current State**:
- LLD docs contain locked definitions (entities, enums, signatures)
- R014 prototype demonstrates working patterns but scattered structure
- Mimicus provides Clean Architecture reference implementation
- Standard OpenSpec workflows require manual artifact creation

**Constraints**:
- CLAUDE_POLICY.md enforces absolute imports, 100-line file limits
- Must copy concepts from R014, not names
- Must use ports 8015+ (avoid 8000-8014)
- All changes must pass ruff, pyrefly checks

**Stakeholders**:
- Implementation: Developers building Real AgentX
- Validation: CLAUDE_POLICY.md enforcement
- Reference: Mimicus patterns, LLD locked definitions

## Goals / Non-Goals

**Goals**:
- Automate spec discovery via LLD synthesis and opsx:explore
- Generate comprehensive specs without manual file enumeration
- Validate all outputs against CLAUDE_POLICY.md
- Produce consistent artifact quality across all changes

**Non-Goals**:
- Implementing the actual AgentX code (this is spec generation only)
- Modifying LLD documents (they are source of truth)
- One-size-fits-all schema (specifically designed for AgentX context)

## Decisions

### 1. 7-Artifact Pipeline

**Decision**: Sequential pipeline: scan → extract → validate → proposal → specs → design → tasks

**Rationale**:
- **scan**: Must happen first to discover what exists
- **extract**: Categorizes patterns before validation
- **validate**: Policy checks before committing to proposal
- **proposal/specs/design/tasks**: Standard OpenSpec flow

**Alternatives Considered**:
- **Single artifact**: Too much cognitive load, hard to review
- **Parallel artifacts**: Dependencies make ordering critical
- **5 artifacts**: Removed validation (rejected - policy compliance required)

### 2. Template-Based Generation

**Decision**: Each artifact has a Markdown template with placeholder variables

**Rationale**:
- Templates provide structure without dictating content
- Markdown is human-readable and version-controllable
- Placeholders (`{{change_name}}`) allow automation

**Alternatives Considered**:
- **JSON/YAML templates**: Less readable for non-technical stakeholders
- **No templates**: Too much variation between changes

### 3. opsx:explore Integration

**Decision**: scan.md orchestrates opsx:explore with forced topics and absolute paths

**Rationale**:
- opsx:explore provides AI-assisted codebase discovery
- Forced topics ensure comprehensive coverage
- Absolute paths work around explore mode limitations

**Alternatives Considered**:
- **Manual file enumeration**: Infeasible at 200+ files
- **Glob patterns**: Misses context and relationships

### 4. LLD as Source of Truth

**Decision**: All locked definitions (entities, enums, signatures) come from LLD docs

**Rationale**:
- LLD is already reviewed and locked
- Prevents drift between spec and implementation
- Single source of truth principle

**Alternatives Considered**:
- **Extract from prototypes**: R014 has issues, not authoritative
- **Duplicate definitions**: Violates DRY, risks divergence

## Risks / Trade-offs

### Risk: Template Rigidity

**Risk**: Templates may not fit all change types

**Mitigation**:
- Templates use generic structure with flexible content areas
- Can evolve templates based on C001-C006 experience

### Risk: opsx:explore Variability

**Risk**: AI exploration may produce inconsistent results

**Mitigation**:
- Use forced topics for consistency
- Cross-validate with LLD locked definitions
- Human review at each artifact

### Trade-off: Automation vs Control

**Trade-off**: More automation reduces manual work but increases abstraction

**Decision**: Semi-automated approach
- Templates provide structure
- Human fills in domain-specific content
- Validate step catches policy violations

### Risk: Schema First, Changes Second

**Risk**: Creating schema via spec-driven instead of spec-factory itself

**Mitigation**:
- Schema is simple (artifact definitions + templates)
- spec-driven is sufficient for this meta-change
- C001-C006 will validate spec-factory workflow

## Migration Plan

**Steps**:
1. ✅ Create spec-factory schema structure
2. ✅ Write schema.yaml with 7 artifact definitions
3. ✅ Create all 7 templates
4. 🔄 Create change for spec-factory itself (using spec-driven)
5. ⏭️ Use spec-factory for C001-C006 changes

**Rollback Strategy**:
- If spec-factory doesn't work: Fall back to spec-driven for each change
- Schema is additive: Doesn't break existing workflows

## Open Questions

1. **Should templates be versioned?**
   - Decision: Schema version in schema.yaml, templates evolve with project

2. **Should extract generate multiple draft specs?**
   - Decision: Yes, but human curates before specs phase

3. **How to handle spec-factory schema updates?**
   - Decision: Create separate change when templates need evolution
