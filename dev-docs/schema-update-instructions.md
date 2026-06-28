# Schema Update Workflow

Canonical planning docs live in dev-docs/plans:

- master plan: dev-docs/plans/master-plan.md
- roadmap: dev-docs/plans/roadmap.md

Use this document when a new SDE build introduces schema or data changes.

## Preconditions

- Use the repository virtual environment: ./.venv
- Choose a working directory for artifacts, for example:
	- dev-data/tmp/sde-update/<build_number>/
- Keep both YAML and JSONL variants when possible so parity checks can be run.

## 1) Fetch metadata and changelogs

Save latest info, schema changelog, and data changelog first.

```bash
esd metadata latest --file-out dev-data/tmp/sde-update/latest.json
esd metadata schema-changes --file-out dev-data/tmp/sde-update/schema-changelog.yaml
esd metadata data-changes --file-out dev-data/tmp/sde-update/data-changes.jsonl
```

If the build number is known, include --build-number on schema-changes and data-changes.

## 2) Download and extract SDE variants

```bash
esd zip download-yaml dev-data/tmp/sde-update/zips
esd zip download-jsonl dev-data/tmp/sde-update/zips
esd zip extract dev-data/tmp/sde-update/zips/<yaml-zip-file> dev-data/tmp/sde-update/extracted --use-build-number
esd zip extract dev-data/tmp/sde-update/zips/<jsonl-zip-file> dev-data/tmp/sde-update/extracted --use-build-number
```

Expected result: extracted datasets are available under the selected build folder.

## 3) Generate schema reports for inspection

Prefer the dev schema-report commands for file-level schema comparison.

```bash
esd dev schema-report files dev-data/tmp/sde-update/extracted/<build>/sde/yaml --format yaml --report-path dev-data/tmp/sde-update/reports --overwrite
esd dev schema-report files dev-data/tmp/sde-update/extracted/<build>/sde/jsonl --format jsonl --report-path dev-data/tmp/sde-update/reports --overwrite
```

Review added or removed dataset files and field changes before code edits.

## 4) Run validation workflows

For YAML file validation:

```bash
esd validate yaml-files dev-data/tmp/sde-update/extracted/<build>/sde/yaml --report-path dev-data/tmp/sde-update/validation --overwrite
```

For DB-backed validation (after DB import):

```bash
esd db from-yaml dev-data/tmp/sde-update/extracted/<build>/sde/yaml dev-data/tmp/sde-update/db --overwrite
esd validate yaml-db dev-data/tmp/sde-update/db/<db-file>.db --report-path dev-data/tmp/sde-update/validation --overwrite
```

## 5) Update code for schema changes

When a new dataset appears:

1. Add dataset filename mappings in src/eve_static_data/models/dataset_filenames.py.
2. Add or update models in src/eve_static_data/models/yaml_format/.
3. Update loader lookups and access methods in src/eve_static_data/record_loader/.
4. Update DB import/table logic if required in src/eve_static_data/db/.
5. Add or update tests in tests/eve_static_data/ matching touched modules.

When fields change in an existing dataset:

1. Update model fields and aliases.
2. Re-run validation reports.
3. Confirm exports and derived data paths still pass tests.

## 6) Refresh fixture test data

Use the dev fixture generator for small deterministic fixtures.

```bash
esd dev generate-test-data files dev-data/tmp/sde-update/extracted/<build>/sde/yaml tests/resources/sde_data --format yaml --overwrite
esd dev generate-test-data files dev-data/tmp/sde-update/extracted/<build>/sde/jsonl tests/resources/sde_data/jsonl --format jsonl --overwrite
```

If fixture layout changes, update tests that rely on older fixture paths.

## 7) Finalize build metadata

After validation passes, update build constants in src/eve_static_data/__init__.py:

- AFTER_BUILD_NUMBER
- RELEASE_DATE

Values should match the authoritative latest metadata/changelog content used above.

## 8) Verification checklist

- Schema reports generated for target formats.
- Validation reports generated and reviewed.
- Targeted tests for touched modules pass.
- Full test suite pass is clean.
- Canonical plan status updated in dev-docs/plans/master-plan.md.
