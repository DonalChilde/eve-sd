<!-->TODO these steps need to be updated and validated.<-->

# Steps for updating the eve-static-data code with a new schema.

## Download and validate the new SDE dataset.
- Download the yaml version of the dataset (and the jsonl version, when that is completed.)
- Export the unpacked dataset to json - The yaml versions load very slow.
- Validate the json versions, check for errors.
- Export new sets of test data. yaml, json, (jsonl, and json when jsonl support completed)

## New dataset.

- reference the textual report, check for new dataset files.
- Add the file to dataset_filenames.py
- Add a new model to the records model file, eg. yaml_records.py
- Add a new RootModel for dataset eg. yaml_datasets.py
- Add file-to-model lookup entry in dataset module
- Add new access function to loader.
- Add new test case to test_yaml_records.py



- rerun validation report and check for errors
- update AFTER_BUILD_NUMBER and RELEASE_DATE IN `__init__.py` using values from schema_changelog.yaml
