# """Validation functions for EVE Static Data Export (SDE) datasets loaded from a SQLite database."""

# import sqlite3

# from whenever import Instant

# from eve_static_data.models.dataset_filenames import SdeDatasets
# from eve_static_data.record_loader.yaml_format import YamlDBLoader
# from eve_static_data.validation.models import (
#     DatasetValidationResult,
#     SdeValidationSummary,
# )
# from eve_static_data.validation.yaml_validation import (
#     validate_yaml_dataset,
# )


# def validate_yaml_datasets_db(connection: sqlite3.Connection) -> SdeValidationSummary:
#     """Validate all YAML datasets in the given SDE path and return a summary of results.

#     Args:
#         connection: A SQLite database connection to the SDE database.

#     Returns:
#         A summary of the validation results for all datasets.
#     """
#     loader = YamlDBLoader(connection)
#     started_timestamp_nanos = Instant.now().timestamp_nanos()
#     sde_metadata = loader.sde_metadata()
#     dataset_key_types = loader.dataset_key_types

#     validation_results: dict[str, DatasetValidationResult] = {}
#     provided_dataset_names: set[str] = set(dataset_key_types.keys())
#     expected_dataset_names: set[str] = set(item.value for item in SdeDatasets)

#     for dataset_name in dataset_key_types.keys():
#         if dataset_name not in expected_dataset_names:
#             continue  # Skip unexpected dataset files
#         dataset_enum = SdeDatasets(dataset_name)
#         raw_records = loader.load_raw_records(dataset_enum, record_keys=None)
#         validation_result = validate_yaml_dataset(
#             dataset_enum=dataset_enum,
#             raw_records=raw_records,
#         )
#         validation_results[dataset_enum.value] = validation_result

#     return SdeValidationSummary(
#         sde_metadata=sde_metadata,
#         started_timestamp_nanos=started_timestamp_nanos,
#         finished_timestamp_nanos=Instant.now().timestamp_nanos(),
#         expected_datasets=len(expected_dataset_names),
#         validated_datasets=len(validation_results),
#         missing_datasets=expected_dataset_names - provided_dataset_names,
#         unexpected_datasets=provided_dataset_names - expected_dataset_names,
#         validation_results=validation_results,
#     )
