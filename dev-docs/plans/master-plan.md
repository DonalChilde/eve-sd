# Master Plan

This is the execution-focused source of truth for current project work.

## Primary Outcome

Stabilize CLI and core API behavior so the package is reliable for download,
validation, import, and scripted local workflows.

## Planning Principles

- Prefer small, shippable milestones over broad parallel efforts.
- Keep implementation and docs aligned as part of each milestone.
- Defer large UX initiatives until core data workflows are stable.

## Current Scope

### In Scope

- Dev CLI tooling (schema inspection, test data generation entry points)
- Public API cleanup and explicit supported surface
- Documentation consolidation and update workflows
- Validation and report workflow reliability

### Out of Scope (for now)

- Textual TUI implementation
- Major CI or release pipeline redesign
- Broad feature expansion unrelated to stabilization goals

## Accomplished Baseline

### CLI and network workflows

- SDE metadata retrieval (latest info, changelog resources)
- SDE download, unpack, and variant handling
- Export commands for YAML to JSON and JSONL to JSON

### Validation and reporting

- YAML validation from files and DB
- Markdown and JSON report generation

### Data access and persistence

- YAML and JSONL import paths to SQLite
- Dataset table definitions and helper query infrastructure

### Test foundation

- Established pytest coverage for DB, validation, models, and helper modules

## Known Gaps and Risks

- JSONL record loading/validation path is incomplete in parts of loader surface.
- Public package API boundary still needs broader usage examples.
- New dev commands need deeper behavioral test coverage.
- Schema update workflow is updated, but should be exercised on the next schema release.
- Planning information is distributed across multiple legacy docs.

## Active Milestones

### M1: Public API Cleanup

Goal: define and document a stable, intentional import surface.

### Tasks

- Audit package exports and identify supported top-level objects.
- Update package export list and remove ambiguous TODO surface.
- Add a short API usage section in docs.

### Done Criteria

- Top-level exports are explicitly listed and justified.
- API docs match real imports and examples run as written.

### M2: Dev CLI Tooling Baseline

Goal: provide first-class developer commands for recurring maintenance tasks.

### Tasks

- Add dev command group to main CLI registration.
- Add initial commands for schema report generation and test data generation.
- Add command help text and usage examples.

### Done Criteria

- Dev commands are discoverable in CLI help output.
- Each dev command has basic tests or manual verification notes.

### M3: Documentation Consolidation

Goal: reduce drift by aligning docs around this plan.

### Tasks

- Align schema update instructions with current code paths.
- Cross-link legacy planning docs to this canonical plan.
- Add a lightweight update checklist for future schema releases.

### Done Criteria

- Canonical docs are internally consistent.
- Update flow is reproducible from docs without guesswork.

### M4: JSONL Parity (Next)

Goal: complete JSONL parity for model-backed loading and validation integration.

### Tasks

- Finish missing loader/model paths.
- Reuse current report structures for JSONL validation output.
- Add focused tests for JSONL parity behavior.

### Done Criteria

- JSONL workflows no longer rely on placeholder stubs.
- Validation results are produced in the same shape as existing reports.

### M5: Data Access and Derived Dataset Expansion (Later)

Goal: improve convenience and performance once stabilization is complete.

### Candidate Tasks

- Selected derived datasets (for example region/location name maps)
- Additional export shaping as needed for common workflows
- Incremental loader performance improvements

## Execution Loop

This section should be updated continuously during active work.

### Current Focus

- M2 Dev CLI tooling baseline
- M1 Public API cleanup
- M4 JSONL parity prep

### Done Recently

- Created canonical planning docs in dev-docs/plans.
- Added dev CLI command group with schema-report and generate-test-data commands.
- Added baseline CLI tests for dev command registration and failure paths.
- Updated schema update instructions to a current, executable workflow.
- Added canonical-plan pointers in legacy roadmap and refactor docs.

### Next Up

1. Wire dev command group into CLI.
2. Add success-path tests for new dev commands with small sample datasets.
3. Add short public API usage examples in README.
4. Start JSONL parity task breakdown under M4.
