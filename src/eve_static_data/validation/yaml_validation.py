"""Validation logic for YAML datasets."""

from collections.abc import Iterable
from time import perf_counter_ns

from pydantic import ValidationError
from whenever import Instant

from eve_static_data.helpers.sde_metadata import SdeMetadata
from eve_static_data.models.dataset_filenames import SdeDatasets
from eve_static_data.models.yaml_datasets import datasets_to_root_model_lookup
from eve_static_data.validation.models import (
    DatasetInput,
    DatasetValidationResult,
    FailedRecordValidation,
    SdeValidationSummary,
)

# TODO implement source media detection and include in summary results- include in SdeMetadata?


def validate_yaml_datasets(
    datasets: Iterable[DatasetInput],
    sde_metadata: SdeMetadata,
) -> SdeValidationSummary:
    """Validate YAML datasets against pydantic models and return a summary of results.

    For each datset, this function looks up the corresponding RootModel class, then
    validates each top-level record in the dataset against that model. Validation errors
    are collected and included in the final summary.

    Args:
        datasets: An iterable of dataset inputs, each containing the dataset name and data.
        sde_metadata: Metadata for the SDE being validated.

    Returns:
        A summary of the validation results.
    """
    validation_results: dict[str, DatasetValidationResult] = {}
    provided_dataset_names: set[str] = set()
    expected_dataset_names: set[str] = set(item.value for item in SdeDatasets)
    unexpected_dataset_names: set[str] = set()
    for dataset_input in datasets:
        dataset_name = dataset_input["dataset_name"]
        provided_dataset_names.add(dataset_name)
        dataset_data = dataset_input["dataset_data"]
        try:
            dataset_enum = SdeDatasets(dataset_name)
        except ValueError:
            # Skip datasets that are not part of the expected SDE datasets
            unexpected_dataset_names.add(dataset_name)
            continue
        root_model_lookup = datasets_to_root_model_lookup()
        root_model_class = root_model_lookup.get(dataset_enum)
        if root_model_class is None:
            raise ValueError(f"No RootModel class found for dataset {dataset_name}")
        start = perf_counter_ns()
        validation_failures: list[FailedRecordValidation] = []
        for record_key, record_data in dataset_data.items():
            test_record = {record_key: record_data}
            try:
                root_model_class.model_validate(test_record)
            except ValidationError as ve:
                validation_failures.append(
                    FailedRecordValidation(
                        dataset=dataset_name,
                        top_level_key=record_key,
                        error_messages=[str(x) for x in ve.errors()],
                    )
                )

            except Exception as e:
                validation_failures.append(
                    FailedRecordValidation(
                        dataset=dataset_name,
                        top_level_key=record_key,
                        error_messages=[f"Unexpected error: {str(e)}"],
                    )
                )
        validation_result = DatasetValidationResult(
            dataset=dataset_name,
            source_format="yaml-model",
            record_count=len(dataset_data),
            validation_time_nanoseconds=perf_counter_ns() - start,
            failed_records=validation_failures,
        )
        validation_results[dataset_name] = validation_result
    return SdeValidationSummary(
        sde_metadata=sde_metadata,
        source_format="yaml-model",
        source_media="yaml-file",
        generated_at_utc=Instant.now().format_iso(),
        expected_datasets=len(SdeDatasets),
        validated_datasets=len(validation_results),
        missing_datasets=expected_dataset_names - provided_dataset_names,
        unexpected_datasets=unexpected_dataset_names,
        validation_results=validation_results,
    )
