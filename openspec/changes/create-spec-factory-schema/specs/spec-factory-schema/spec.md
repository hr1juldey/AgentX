# Spec: spec-factory-schema

**Capability**: Custom OpenSpec schema for automated spec generation

## ADDED Requirements

### Requirement: Schema definition
The spec-factory schema SHALL be defined at `openspec/schemas/spec-factory/schema.yaml` and contain a 7-artifact pipeline definition.

#### Scenario: Schema file exists
- **WHEN** OpenSpec loads schemas
- **THEN** `spec-factory` is available as a schema option
- **AND** schema.yaml contains 7 artifact definitions in order

#### Scenario: Artifact sequence
- **WHEN** creating a change with spec-factory schema
- **THEN** artifacts are generated in order: scan, extract, validate, proposal, specs, design, tasks

### Requirement: Template availability
Each artifact SHALL have a corresponding Markdown template in `openspec/schemas/spec-factory/templates/`.

#### Scenario: All templates exist
- **WHEN** spec-factory schema is installed
- **THEN** templates/scan.md exists
- **AND** templates/extract.md exists
- **AND** templates/validate.md exists
- **AND** templates/proposal.md exists
- **AND** templates/specs.md exists
- **AND** templates/design.md exists
- **AND** templates/tasks.md exists

### Requirement: Scan artifact
The scan artifact SHALL synthesize LLD documents and orchestrate opsx:explore to generate file inventory and discover patterns.

#### Scenario: LLD synthesis
- **WHEN** creating scan.md for a change
- **THEN** locked definitions are extracted from LLD docs
- **AND** entities are listed from domain_model.md
- **AND** signatures are listed from agent_runtime.md
- **AND** enums are documented with values

#### Scenario: Codebase exploration
- **WHEN** creating scan.md
- **THEN** opsx:explore is invoked with absolute paths
- **AND** forced topics cover architecture, patterns, anti-patterns
- **AND** file inventory includes line counts and purposes

### Requirement: Extract artifact
The extract artifact SHALL categorize discovered patterns and generate specification drafts.

#### Scenario: Pattern catalog
- **WHEN** creating extract.md
- **THEN** architectural patterns are listed (Clean Architecture, Repository, etc.)
- **AND** code structure patterns are documented (@dataclass, ABC repos, DTOs)
- **AND** R014 naming patterns to avoid are identified
- **AND** mimicus patterns are referenced (concepts, not names)

#### Scenario: Spec drafts
- **WHEN** creating extract.md
- **THEN** draft specs are generated for each domain
- **AND** API contracts are documented (REST, WebSocket, ports)
- **AND** Pydantic → Zod mappings are listed

### Requirement: Validate artifact
The validate artifact SHALL check outputs against CLAUDE_POLICY.md and assess spec quality.

#### Scenario: Policy compliance
- **WHEN** creating validate.md
- **THEN** import rules are checked (no relative imports)
- **AND** Ruff compliance is verified (check, format)
- **AND** file size limits are enforced (100 + 50)
- **AND** anti-patterns are flagged (god objects, magic numbers)

#### Scenario: LLD alignment
- **WHEN** creating validate.md
- **THEN** entity definitions match domain_model.md
- **AND** enum values match LLD exactly
- **AND** signatures match agent_runtime.md
- **AND** deviations are justified

### Requirement: Template structure
Each template SHALL provide structured sections with placeholder variables for automated content generation.

#### Scenario: Template variables
- **WHEN** templates are processed
- **THEN** `{{change_name}}` is replaced with actual change name
- **AND** `{{timestamp}}` is replaced with generation timestamp
- **AND** `{{domain}}` is replaced with domain-specific content

### Requirement: Schema versioning
The schema SHALL include a version number in schema.yaml for evolution tracking.

#### Scenario: Version identification
- **WHEN** reading spec-factory schema
- **THEN** version field exists in schema.yaml
- **AND** version format is semver (e.g., 1.0.0)

### Requirement: Dependency handling
Artifact dependencies SHALL be explicitly defined to enforce correct generation order.

#### Scenario: Sequential dependencies
- **WHEN** artifacts depend on previous outputs
- **THEN** extract depends on scan
- **AND** validate depends on extract
- **AND** proposal depends on validate
- **AND** specs depends on proposal
- **AND** design depends on proposal
- **AND** tasks depends on design and specs

## REMOVED Requirements

None (new capability)

## MODIFIED Requirements

None (new capability)

## RENAMED Requirements

None (new capability)
