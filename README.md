# EVE Static Data

`eve-static-data` provides a command-line workflow and Python API for working
with the EVE Online Static Data Export (SDE).

The CLI entrypoint is `eve-sd`.

```bash
eve-sd --help
```

## What This App Does

Core capabilities:

- Fetch SDE metadata and changelogs from the official endpoint.
- Download SDE archives by build number and variant (`yaml` or `jsonl`).
- Unpack SDE archives into local directories.
- Build a local SQLite database from unpacked SDE files.
- Browse records in the SQLite database from the CLI.
- Generate schema reports from dataset files or an existing database.
- Convert SDE files between formats for downstream tooling.
- Access data programmatically through a typed Python query API.

## Typical Workflow

Most users follow this sequence:

1. Fetch the latest build information.
2. Download an archive.
3. Unpack the archive.
4. Build a SQLite database.
5. Query data from the CLI or Python.

### 1) Fetch Latest Build Info

```bash
eve-sd fetch latest
```

Optional: write output to disk.

```bash
eve-sd fetch latest --to ./metadata --file-name latest_sde_info.json
```

### 2) Download an SDE Archive

Download the latest YAML variant:

```bash
eve-sd fetch sde --to ./downloads --variant yaml
```

Download a specific build:

```bash
eve-sd fetch sde --to ./downloads --variant jsonl --build-number 3419624
```

### 3) Unpack the Archive

```bash
eve-sd unpack --from ./downloads/eve-online-static-data-3419624-yaml.zip --to ./sde
```

By default, unpack uses a build-number subdirectory, for example
`./sde/3419624`.

### 4) Create a Database from Unpacked Data

```bash
eve-sd db create --from ./sde/3419624 --to ./db --file-name sde_3419624.db
```

Defaults:

- If `--file-name` is omitted, a name based on build and variant is generated.
- If `--serialization-format` is omitted, the app chooses:
    - `json` for JSONL source data
    - `pickle` for YAML source data

### 5) Browse the Database in the CLI

List datasets with record counts and key types:

```bash
eve-sd db browse --from ./db/sde_3419624.db
```

Browse a dataset page:

```bash
eve-sd db browse --from ./db/sde_3419624.db --dataset types --page-size 5 --page 1
```

Fetch specific records:

```bash
eve-sd db browse --from ./db/sde_3419624.db --dataset types --record-key 34 --record-key 35
```

## Changelog Commands

Fetch data changelog:

```bash
eve-sd fetch data-changes --build-number 3419624
```

Fetch schema changelog:

```bash
eve-sd fetch schema-changes --build-number 3419624
```

Both commands can print to stdout or write to disk using `--to` and optional
`--file-name`.

## Schema Reports

Generate a schema report directly from unpacked files:

```bash
eve-sd schema report files --from ./sde/3419624 --stdout-format markdown
```

Generate a schema report from an existing database:

```bash
eve-sd schema report db --from ./db/sde_3419624.db --stdout-format json
```

Write report files to a directory:

```bash
eve-sd schema report files --from ./sde/3419624 --to ./reports --overwrite
```

## Format Conversion Commands

Convert YAML datasets to JSON:

```bash
eve-sd export yaml-to-json --from ./sde/3419624 --to ./json
```

Convert JSONL datasets to JSON with dictionary output keyed by `_key`:

```bash
eve-sd export jsonl-to-json --from ./sde/3419624 --to ./json
```

Use list output when needed:

```bash
eve-sd export jsonl-to-json --from ./sde/3419624 --to ./json --container list
```

## Programmatic API Usage

Expected pattern: create the SQLite database with the CLI first, then use the
Python API to query it.

### API Example: create_read_write_connection + DatasetDbQuery

```python
from pathlib import Path

from eve_static_data.db.helpers import create_read_write_connection
from eve_static_data.db.query import DatasetDbQuery

db_path = Path("./db/sde_3419624.db").resolve()

with create_read_write_connection(str(db_path)) as connection:
    query = DatasetDbQuery(connection)

    # Inspect metadata and dataset catalog
    print("SDE metadata:", query.sde_metadata)
    print("Dataset count:", len(query.dataset_key_types))

    # Query one dataset (adjust name as needed for your DB)
    dataset_name = "types"
    record_count = query.dataset_record_count(dataset_name)
    print(f"{dataset_name} record count:", record_count)

    # Read first 10 records from an integer-keyed dataset
    for record_key, record in query.get_int_records_page(
        dataset_name,
        limit=10,
        offset=0,
    ):
        print(record_key, record)
```

If you need a mapping instead of an iterator of `(key, record)` tuples:

```python
records = query.as_dict(query.get_int_records_page("types", limit=100, offset=0))
print(len(records))
```

## Common Notes

- `DatasetDbQuery` validates dataset existence and key type before querying.
- Record-key type (`int` or `str`) is tracked per dataset in the DB metadata.
- Some commands emit rich progress/status messages unless `--quiet` is used.

## Installation

PyPI deployment is not enabled yet. Install from github with `uv`, or work from a
local source checkout.

### Install with `uv`

Run the CLI directly from the repository without installing it globally:

```bash
uvx --from git+https://github.com/DonalChilde/eve-static-data@main eve-sd --help
```

Install the command into your `uv` tool path:

```bash
uv tool install --from git+https://github.com/DonalChilde/eve-static-data@main eve-static-data
eve-sd --help
```

### Install from Source

```bash
git clone https://github.com/DonalChilde/eve-static-data.git
cd eve-static-data
uv sync
source .venv/bin/activate
eve-sd --help
```

You can also run the project directly through `uv` without activating the
virtual environment:

```bash
uv run eve-sd --help
```

## Useful Utility Commands

Show version:

```bash
eve-sd version
```

Show effective runtime settings:

```bash
eve-sd settings
```

Show the in-app documentation:

```bash
eve-sd docs
```

## Development Notes

Development dependencies are managed with `uv`. See `pyproject.toml` for the
current lint and test configuration.

## License

MIT License. See [LICENSE](LICENSE) for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.
