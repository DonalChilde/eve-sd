# Eve Static Data

eve static data is a cli/api forcused app for interacting with the EVE Online SDE.

## Features

### General

- Provides a cli to download, unpack, and inspect the SDE.
- Can import the SDE to a SQLite database, allowing per record access based on record key.
- Can access datasets as raw data, or via validated dataclasses
- Can check the latest available version number of the SDE
- Can download the latest schema and dataset changes.
- Can export yaml and jsonl datasets to json.
- Can export some commonly used data subsets.
- Database records can be round tripped to file records. record order not guaranteed, but actual data is.
  - use pickle
- Schema report can be used to generate TypedDict schema for most records
  - Exception for datasets where the field name is an int. This is not valid for a python typeddict.
    - how to handle? re. masteries.yaml
- can page through dataset records via cli.
- db stores schema report, changes, and validation report - based on db records, not files.

### CLI

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
