# """Validation functions for EVE Static Data Export (SDE) datasets loaded from files."""

# from collections.abc import Iterable
# from pathlib import Path
# from typing import Any

# from whenever import Instant

# from eve_static_data.helpers import json_io, yaml_io
# from eve_static_data.helpers.sde_metadata import SdeMetadata, load_sde_metadata
# from eve_static_data.models.dataset_filenames import SdeDatasets
# from eve_static_data.validation.models import (
#     DatasetValidationResult,
#     SdeValidationSummary,
# )
# from eve_static_data.validation.yaml_validation import (
#     validate_yaml_dataset,
# )


# def validate_yaml_datasets_file(sde_path: Path) -> SdeValidationSummary:
#     """Validate all YAML datasets in the given SDE path and return a summary of results.

#     Args:
#         sde_path: Path to the SDE directory containing YAML dataset files.

#     Returns:
#         A summary of the validation results for all datasets.
#     """
#     started_timestamp_nanos = Instant.now().timestamp_nanos()
#     sde_metadata = load_sde_metadata(sde_path)
#     glob_pattern = f"*{sde_metadata.source_media}"
#     dataset_files = list(sde_path.glob(glob_pattern))

#     validation_results: dict[str, DatasetValidationResult] = {}
#     provided_dataset_names: set[str] = set(
#         dataset_file.stem for dataset_file in dataset_files
#     )
#     expected_dataset_names: set[str] = set(item.value for item in SdeDatasets)

#     for dataset_file in dataset_files:
#         if dataset_file.stem not in expected_dataset_names:
#             continue  # Skip unexpected dataset files
#         dataset_enum = SdeDatasets(dataset_file.stem)
#         validation_result = validate_yaml_dataset(
#             dataset_enum=dataset_enum,
#             raw_records=_yield_records_from_file(
#                 dataset_file, sde_metadata=sde_metadata
#             ),
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


# def _yield_records_from_file(
#     file_path: Path,
#     sde_metadata: SdeMetadata,
# ) -> Iterable[tuple[str | int, dict[str, Any]]]:
#     """Yield (key, record_dict) tuples from a YAML dataset file.

#     Will load datasets from .yaml or .json files.
#     """
#     match sde_metadata.source_media:
#         case ".yaml":
#             raw_records_dict = yaml_io.safe_load_path(file_path)
#         case ".json":
#             raw_records_dict = json_io.json_load_path(file_path)
#         case ".jsonl":
#             raise ValueError(
#                 f"Expected a YAML or JSON file for dataset '{file_path}', but got "
#                 "JSONL. Use the JSONL loader instead."
#             )
#         case ".db":
#             raise ValueError(
#                 f"Expected a YAML or JSON file for dataset '{file_path}', but got "
#                 "SQLite database. Use the SQLite loader instead."
#             )
#         case _:
#             raise ValueError(
#                 f"Unsupported source media '{sde_metadata.source_media}' for dataset '{file_path}'."
#             )
#     if raw_records_dict is None:
#         raise ValueError(f"Dataset file '{file_path}' is empty or could not be loaded.")
#     if not isinstance(raw_records_dict, dict):
#         raise ValueError(
#             f"Expected a YAML mapping (dict) in file '{file_path}', but got {type(raw_records_dict).__name__}."
#         )
#     yield from raw_records_dict.items()
