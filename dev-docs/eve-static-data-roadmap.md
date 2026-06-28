# EVE Static Data Roadmap

Note: active execution planning now lives in dev-docs/plans/master-plan.md.
This roadmap file is retained as legacy context and idea history.

EVE Static Data is a cli program used to download, validate, access, and export the EVE static dataset.

Typical Flow:

- Download the latest SDE data
  - data is unzipped and initially verified, checking for \_sde and a build number
  - unzipped data is copied to the data directory, normally `<app_dir>/data/<buildnumber>/sde/`
  - data is validated, and the validation report saved to `<app_dir>/data/<buildnumber>/validation/`
  - derived datasets are generated, and saved to `<app_dir>/data/<buildnumber>/derived/<lang>/`
- Derived datasets exist to save memory later, as they are either cut down datasets for common operations like region name lookups, or combined datasets like normailzed_types. Derived datasets are also localized.
- Top level api access will load the various dataset types - Typeddict, Pydantic, Localized, derived
  - app provides configured SdeReader, and derived dataset loader. Use dataset Models to load non derived data ,`<Dataset>.from_sde(reader)`
- Downloading a new SDE Dataset will not delete the old one automatically
- the CLI provides info on how many datasets are available, and tools to erase them.

## Features

- [x] Check for the latest available version of the SDE, ref build number and release date.
- [x] Download and display the SDE schema changelog.
- [x] Download the SDE and save to file.
- [x] Generate and save a summary of the available fields in the datasets, used in TypedDict schema generation.
- [x] Offer a pydantic schema for the SDE.
- [x] Offer a TypedDict schema for the SDE.
- [x] Validate the SDE against a Pydantic schema.
  - [x] Create a Pydantic representaion of the SDE dataset.
  - [x] collect data on the validation status of the SDE
    - [x] display data in the terminal.
    - [x] Save validation data to a json file.
- [x] Provide an api to iterate over the jsonl records, loaded as TypedDicts.
- [x] Provide an api to iterate over the jsonl records, loaded as Pydantic models.
- [] Offer export of json data from pydantic models.
- [x] Offer an export of localized SDE data as a pydantic backed set of JSON files.
  - [x] Offer lazy loading dataset access api.
    - [] Do this for sde datasets
    - [] Do this for localized datasets
    - [] Do this for exported data
  - [] Include some derived datasets for convenience,
    - [x] Market path
    - [] Location names - eg station names as displayed in game, asteroid belts names, etc.
    - [x] Combined type data table for easy spreadsheet lookups.
  - [] Limited CSV export of some data as appropriate.

### In Progress

- Make a subset of data available for export, expand as needed.
  - more derived datasets like region names
- Make lazy loader for all datasets?
- Make separate Lazy Loader for derived datasets?

## Future possible features

- Sqlite database of full SDE
