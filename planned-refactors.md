# Planned Refactors

Note: active execution priorities are tracked in dev-docs/plans/master-plan.md.
This file remains useful as a backlog of refactor ideas and context.

## NOW

### FIXME
- unpack forces a check for _sde.jsonl, this should be more flexible.

### Add
- functions to detect and load all the _sde variants, used to get buildNumber etc, and to be a quick check that the SDE data exists.
- functions to derive datasets and manipulate SDE datasets?
  - See argus manipulations, move them over?
  - add market_group.types derived dataset to mirror whats available from ESI.
  - make names generator for planets, moons, belts, etc. see online dev docs for format.

### Change
- Export to json takes yaml or jsonl files. 
- Narrow language command to strip unwanted localizatinos from json files. must handle dicts or lists of dicts.



## Next!

### jsonl based validation
- Fully implement jsonl based validation using the current report structure.
- Refactor to use the current yaml record format, localized field access. `_key` field solutions? Dont try to hard to force out pydantic classes, the yaml solution is superior.
- make an access loader?

### Implement a sqlite database to store the sde data.
- each dataset's tables will be self contained, to make it easy to adjust for future sde changes.
- Data is loaded to the database from the pydantic records, but retrieved from the database as vanilla dataclasses.
- Database access functions for each record type, plus the localized records. Minimal filtering supported by the access function, like is_published.
- offer a limited number of derived data function calls.


