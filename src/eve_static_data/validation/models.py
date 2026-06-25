"""Models for validation results and summary of SDE datasets."""

from dataclasses import dataclass, field
from typing import Literal

from eve_static_data.helpers.sde_metadata import SdeMetadata
from eve_static_data.models.dataset_filenames import SdeDatasets


@dataclass(slots=True, kw_only=True)
class FailedRecordValidation:
    """Validation failure details for a single top-level record.

    Attributes:
        dataset: Dataset enum name.
        top_level_key: Top-level key in the source dataset mapping.
        error_messages: Validation messages emitted by pydantic.
    """

    dataset: str
    top_level_key: str | int
    error_messages: list[str]


@dataclass(slots=True, kw_only=True)
class DatasetValidationResult:
    """Validation results for one dataset file."""

    dataset: SdeDatasets
    """The dataset enum name, e.g., SdeDatasets.invTypes."""
    source_format: Literal["yaml-model", "jsonl-model"]
    """The source format of the dataset, either 'yaml-model' or 'jsonl-model'."""
    record_count: int = 0
    """The number of records validated in the dataset."""
    validation_time_nanoseconds: int | None = None
    """The time taken to validate the dataset, in nanoseconds."""
    failed_records: list[FailedRecordValidation] = field(
        default_factory=list[FailedRecordValidation]
    )
    """A list of validation failures for individual records in the dataset."""

    def is_valid(self) -> bool:
        """Return ``True`` when dataset validation has no errors."""
        return len(self.failed_records) == 0


@dataclass(slots=True, kw_only=True)
class SdeValidationSummary:
    """Complete validation result payload for an SDE directory."""

    sde_metadata: SdeMetadata
    """The SDE metadata loaded from the SDE directory."""
    started_timestamp_nanos: int
    """The timestamp (in nanoseconds) when validation started."""
    finished_timestamp_nanos: int
    """The timestamp (in nanoseconds) when validation finished."""
    expected_datasets: int
    """The number of expected datasets based on the SdeDatasets enum."""
    validated_datasets: int
    """The number of datasets that were actually validated."""
    missing_datasets: set[str]
    """The set of expected dataset names that were not validated."""
    unexpected_datasets: set[str]
    """The set of unexpected dataset names that were submitted for validation."""
    validation_results: dict[str, DatasetValidationResult]
    """A mapping of dataset names to their corresponding validation results."""
