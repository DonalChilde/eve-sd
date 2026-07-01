# Eve Static Data

eve static data is a cli/api forcused app for interacting with the EVE Online SDE.

## Features

### General

- Provides a cli to download, unpack, and inspect the SDE.
- Can import the SDE to a SQLite database, allowing per record access based on record key.
- record serialization schema in database can be selected. json, yaml, pickle. Various tradeoffs for each combination of source and scheme
- json serialization uses pydantic
- yaml serialization will use CSafeLoader/CSafeDumper if available
- Can check the latest available version number of the SDE
- Can download the latest schema and dataset changes.
- Can export yaml and jsonl datasets to json.
- Can export some commonly used data subsets.
- Database records can be round tripped to file records. record order not guaranteed, but actual data is.
  - serialization scheme dependent.

- can browse through database dataset records via cli.
  - arg records per page
  - output json or yaml
  - arg keys
- db stores schema report based on db records, not files.

### CLI

#### CLI Shape

Common args:
- --json - output formatted as json
- --yaml - output formatted as yaml
- -q, --quiet - silent output, used for scripts
- --from - arg to accept file or dir path '-' for stdin as appropriate
- --to - arg to accept file or dir path '-' for stdout as appropriate

Make progress bar

- Entry Point - eve-sd
  - Args
    - verbosity?
  - Command - version - Show the version of eve-sd
  - Command - fetch - Fetch network resources
    - Command - latest-info - fetch latest sde version info
    - Command - schema-changes - fetch the schema changes for a schema build number
      - Arg - -b, --build-number - The build number to fetch, if not provided, fetch latest.
    - Command - data-changes - fetch the data changes for a schema build number
      - Arg - -b, --build-number - The build number to fetch, if not provided, fetch latest.
    - Command - sde - download the sde zip file.
      - Arg - -b, --build-number
      - Arg - --format yaml|jsonl defaults to yaml
  - Command - unpack - unzips an SDE zip file - extract to folder with optional default naming
  - Command - schema - commands for generating schema reports
    - Command - files - Generate a schema report froma set of SDE files.
    - Command - db - Generate a report from a db. option to update report on db. option to force update report on db.
  - Command - dev - commands mostly only useful for dev work
    - Command - test-data - generate test data from a set of files, or db.
    - Command - perf - generate perf report from files or db. json and markdown report.
    - Command - compare - Prove files data matches db data. json and markdown report.
  - Command - db - Commands for working with sde db
    - Command - create - create a sde db from a set of sde files.
    - Command - browse - browse db datasets
    - Command - report - commands to report on various parts of the db
      - Command - schema - commands to display or export db schema-report
      - Command - datasets - report on the dataset-names, record-key types, and record counts
      - Command - stats? - report on the serialization scheme, size?


- [x] Download the SDE zip file to disk
  - [x] Can select build number. Defaults to latest.
  - [x] Can select the datamodel format. JSONL or YAML. Defaults to yaml.
- [x] unpack the SDE zip file, with optional naming based on the SDE build number.
- [] Inspect the unpacked SDE
  - [x] Inspect the schema of each dataset, report on fields and data types.
  - [x] Download and display or save the schema changelog
  - [x] Download and save or display the SDE dataset changes
  - [] Validate the SDE datasets and report results
    - [x] yaml datasets
    - jsonl datasets
  - [] rollup command to do all inspections and save reports.
    - [x] yaml datasets
    - [] jsonl datasets
  - [x] Import SDE files to a SQLite database.
    - [x] yaml
    - [x] jsonl
- [] Export vairous data subsets
  - [] Market Path
  - [] type summary
  - [] region names
  - [] solar system names
  - [] market items

### API

- [] Loader classes for various format and source combinations.
  - [] db
    - [] yaml
      - [] raw
      - [] validated dataclasses
    - [] jsonl
      - [] raw
      - [] validated dataclasses
  - [] files
    - [] yaml
      - [] raw
      - [] validated dataclasse
    - [] jsonl
      - [] raw
      - [] validated dataclasse

### Dev Milestones

#### 1 - Foundation

- [x] download and unpack the SDE
- [x] get schema and dataset changes
- [ x ] report on sde dataset schemas
- make dataclasses for validation and use.
  - [x] yaml
  - [ ] jsonl
- validate with report
  - [x] yaml
  - [] jsonl
- CLI for currently supported functions.

#### 2 - Database

- [x] define SQLite database to hold SDE
- [x] import the SDE to the database
- run schema and validation on database SDE, report
- [] CLI for currently supported functions.
  - lacking db validation commands, ?

#### 3 - API

- API access for dataset records.
  - files
    - yaml
    - jsonl
  - db
    - yaml
    - jsonl

#### 4 - Cleanup

- CLI arguments should share the same structure
- Code documentation needs lots of polish.
- Implement testing.
- A usable readme.

#### 5 - Release

Release requirements

- At least one data format is complete from end to end. Right now that looks like the yaml format.
- Testing is green and complete for the public facing code.
- The README is useful, and not embarrasing.
