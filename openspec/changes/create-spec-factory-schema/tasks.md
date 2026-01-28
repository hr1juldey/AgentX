## 1. Schema Structure Setup

- [x] 1.1 Create schema directory: `openspec/schemas/spec-factory/`
- [x] 1.2 Create templates directory: `openspec/schemas/spec-factory/templates/`
- [x] 1.3 Write schema.yaml with 7 artifact definitions
- [x] 1.4 Create scan.md template
- [x] 1.5 Create extract.md template
- [x] 1.6 Create validate.md template
- [x] 1.7 Create proposal.md template
- [x] 1.8 Create specs.md template
- [x] 1.9 Create design.md template
- [x] 1.10 Create tasks.md template

## 2. Change Creation (spec-driven for schema itself)

- [x] 2.1 Create change: "create-spec-factory-schema"
- [x] 2.2 Write proposal.md with schema motivation
- [x] 2.3 Write design.md with technical decisions
- [x] 2.4 Write specs/spec-factory-schema/spec.md
- [x] 2.5 Write tasks.md (this file)

## 3. Verification

- [ ] 3.1 Verify schema is registered with OpenSpec
- [ ] 3.2 Test schema can be selected with `--schema spec-factory`
- [ ] 3.3 Verify all templates are valid Markdown
- [ ] 3.4 Confirm all 7 artifacts are defined in schema.yaml

## 4. Documentation

- [ ] 4.1 Update CLAUDE.md with spec-factory usage instructions
- [ ] 4.2 Document template variable substitutions
- [ ] 4.3 Add spec-factory examples to docs/engineering/

## 5. Next Steps (After This Change)

- [ ] 5.1 Create C001-folder-structure using spec-factory schema
- [ ] 5.2 Create C002-data-contracts using spec-factory schema
- [ ] 5.3 Create C003-agent-pipeline using spec-factory schema
- [ ] 5.4 Create C004-voice-streaming using spec-factory schema
- [ ] 5.5 Create C005-memory-rag using spec-factory schema
- [ ] 5.6 Create C006-release-plan using spec-factory schema

## Definition of Done

This change is complete when:
- [x] All schema files are created and valid
- [x] All change artifacts are written
- [ ] Schema is selectable in OpenSpec
- [ ] Templates work end-to-end (validated by C001)
