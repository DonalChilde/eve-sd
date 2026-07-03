Rough plan notes.

Implement a Textual TUI to interact with the EVE Online SDE.

Accessed through `esd-tui` entry point


Description of problem space:
The EVE online SDE contains 60+ different datasets describing datafro the game.
The datasets are offered in two formats, each representing the same data in slightly different ways.
 - YAML - preferred because of its easier to reason datamodel, due to yaml allowing int dict keys. CON: Very slow load from disk performance.
 - JSONL - Loads very quickly, but the datamodel is less intuitive due to json not allowing int dict keys, the keys are converted to strings.
During load from disc, pydantic models validate the data, and handle any necessary string to int casts.
The zipped sde can be gotten from an API url, by buildNumber and variant
The current available buildNumber, and release date can be gotten from an API url
The schema changelog for a buildnumber can be gotten from an API url
The data changelog for a buildNumber can be gotten from an API url



Capabilities:
Not exhaustive, not necessarily grouped logically.

- download, view, and save the SDE schema changelog
- download, view, and save the SDE changelog
- download, view, and save the latest SDE version info
- downlaod, save, and unpack the SDE data, by buildnumber, and variant.
- export an unpacked SDE from YAML/JSONL to json
- export narrowed localization datasets from the json version.
  - narrow from json because of the supremely poor performance working with yaml. The first step is get to json then work with the data, as to work otherwise might mean loading a yaml dataset more than one time. jsonl does not really have these issues, but a unified interface is preferred.
- validate the YAML/JSONL datamodels against json data, and report.
 - optional save to `validation` in unpacked data
- optional save metadata to `metadata` directory of unpacked data
 - includes schema changelog, sde changelog, for that buildnumber
 - This is currently saved to the same folder as the validation dat in other places in this project, but a future refactory will save it to the `metadata` folder project wide.
- Examine the dataset schemas  of json data, and report
  - optional save to `schemas` directory of unpacked data
- browse datasets in directory, and view the records in a dataset. some datasets are small, and some are quiet large. implement paging? If paging, make page size customizable.

NOTE:
JSONL datamodels are incomplete and not ready for use. Except for export from JSONL to json, other JSONL based activities should be stubs for future expansion.

Organization:
To the largest degree that is sensible, keep tui code in one package/sub-packages
Call out refactors of common code that would make working with the stadard cli, and TUI easier.


Future integrations:
Explore possibility of calling this TUI from another TUI that wants to include this functionality