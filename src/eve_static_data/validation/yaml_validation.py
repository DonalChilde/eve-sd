"""Validation logic for YAML datasets."""

from collections.abc import Iterable
from time import perf_counter_ns
from typing import Any

from pydantic import ValidationError

from eve_static_data.models.dataset_filenames import SdeDatasets
from eve_static_data.models.yaml_format.yaml_records import get_record_model_for_dataset
from eve_static_data.record_loader.yaml_format import deserialize_yaml_record
from eve_static_data.validation.models import (
    DatasetValidationResult,
    FailedRecordValidation,
)


def validate_yaml_dataset(
    dataset_enum: SdeDatasets,
    raw_records: Iterable[tuple[int | str, dict[str, Any]]],
) -> DatasetValidationResult:
    """Validate a single YAML dataset against its corresponding pydantic model."""
    root_model_class = get_record_model_for_dataset(dataset_enum)
    start = perf_counter_ns()
    validation_failures: list[FailedRecordValidation] = []
    count = 0
    for record_key, record_dict in raw_records:
        count += 1
        try:
            record = deserialize_yaml_record(
                root_model_class, record_key=record_key, record_dict=record_dict
            )
            if isinstance(record, ValidationError):
                validation_failures.append(
                    FailedRecordValidation(
                        dataset=dataset_enum,
                        top_level_key=record_key,
                        error_messages=[str(x) for x in record.errors()],
                    )
                )
        except Exception as e:
            validation_failures.append(
                FailedRecordValidation(
                    dataset=dataset_enum,
                    top_level_key=record_key,
                    error_messages=[f"Unexpected error: {str(e)}"],
                )
            )
    validation_result = DatasetValidationResult(
        dataset=dataset_enum,
        source_format="yaml-model",
        record_count=count,
        validation_time_nanoseconds=perf_counter_ns() - start,
        failed_records=validation_failures,
    )
    return validation_result
