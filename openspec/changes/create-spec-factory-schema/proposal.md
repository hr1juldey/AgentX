## Why

Current OpenSpec workflows require manual specification of every detail, which is infeasible for AgentX v0.1 with 200+ Python files across R000-R014 prototypes. We need an automated spec generation pipeline that synthesizes LLD documents and explores the codebase to produce comprehensive specifications without manual enumeration.

## What Changes

**New Custom Schema: spec-factory**
- 7-artifact pipeline: scan → extract → validate → proposal → specs → design → tasks
- Automates LLD synthesis (reads locked entities, enums, signatures from LLD docs)
- Automates codebase exploration via opsx:explore with forced topics
- Generates pattern catalogs from mimicus and R014 reference analysis
- Validates against CLAUDE_POLICY.md (imports, file sizes, anti-patterns)
- Produces domain-specific specs from categorized patterns

**Schema Location**: `/home/riju279/Documents/Code/XRIG/AgentX/openspec/schemas/spec-factory/`

**Templates Created**:
- `scan.md` - LLD synthesis + opsx:explore orchestration
- `extract.md` - Pattern categorization + spec drafts
- `validate.md` - Policy compliance + spec quality checks
- `proposal.md` - Standard OpenSpec proposal
- `specs.md` - Domain-specific specifications
- `design.md` - Technical design with architecture
- `tasks.md` - Implementation checklist

## Capabilities

### New Capabilities
- `spec-factory-schema`: Custom OpenSpec workflow for automated spec generation through LLD synthesis and codebase exploration

### Modified Capabilities
- None (new schema, not modifying existing specs)

## Impact

**Affected Systems**:
- OpenSpec workflow: Adds new schema option for future changes
- Documentation: LLD docs become source of truth for locked definitions

**Dependencies**:
- LLD documents: `docs/engineering/lld/*.md`
- Research docs: `docs/research/*.md`
- R014 prototype: `prototypes/R014_ui_showcase/`
- Mimicus reference: `/home/riju279/Documents/Tools/mimicus/mimicus/src/`

**Enables**:
- Automated generation of C001-C006 specifications
- Reduced manual specification overhead
- Consistent spec quality across all changes
