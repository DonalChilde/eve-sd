# Roadmap

This file tracks future-facing ideas and deferred initiatives.

It is intentionally separate from the active execution work in
[master-plan.md](master-plan.md).

## Near-Term Candidates (after current milestones)

- Complete JSONL parity across loaders, validation, and reporting.
- Add selected derived datasets for common lookups.
- Improve export ergonomics for curated outputs.

## Mid-Term Candidates

- Strengthen DB query ergonomics with practical filtering patterns.
- Expand developer tooling for schema diffing and update prep.
- Add broader end-to-end tests against generated fixture sets.

## Far-Future Initiatives

### Textual TUI

Status: deferred until CLI/API stabilization milestones are complete.

Potential scope:

- Dataset browsing with pagination
- Schema and metadata inspection views
- Validation and report inspection surfaces
- Integrated workflow shortcuts for common SDE tasks

## Parking Lot

- Performance benchmarks comparing YAML, JSONL, and DB-backed access
- Expanded derived exports for spreadsheet/report consumers
- Additional convenience API layers once base API is stable

## Promotion Rule

An item moves from this roadmap into the master plan only when:

1. It supports the current primary outcome.
2. It has concrete done criteria.
3. It does not displace already in-progress stabilization work.
