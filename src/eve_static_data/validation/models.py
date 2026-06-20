from dataclasses import dataclass, field
from typing import Any, Literal, TypedDict

from eve_static_data.helpers.sde_metadata import SdeMetadata


@dataclass
class FailedRecordValidation:
    """Validation failure details for a single top-level record.

    Attributes:
        dataset: Dataset enum name.
        top_level_key: Top-level key in the source dataset mapping.
        error_messages: Validation messages emitted by pydantic.
    """

    dataset: str
    top_level_key: str
    error_messages: list[str]


@dataclass
class DatasetValidationResult:
    """Validation results for one dataset file.

    Attributes:
        dataset: Dataset enum name.
        source_format: Source file format, either "yaml-model" or "jsonl-model".
        record_count: Number of top-level records.
        validation_time_nanoseconds: Elapsed validation time measured by
            ``perf_counter_ns`` in nanoseconds.
        missing_file: Whether no supported source file was found.
        parse_error: Parsing or shape error string if encountered.
        failed_records: Per-record validation errors.
    """

    dataset: str
    source_format: Literal["yaml-model", "jsonl-model"]
    record_count: int = 0
    validation_time_nanoseconds: int | None = None
    parse_error: str | None = None
    failed_records: list[FailedRecordValidation] = field(
        default_factory=list[FailedRecordValidation]
    )

    def is_valid(self) -> bool:
        """Return ``True`` when dataset validation has no errors."""
        return self.parse_error is None and len(self.failed_records) == 0


@dataclass
class SdeValidationSummary:
    """Complete validation result payload for an SDE directory."""

    sde_metadata: SdeMetadata
    generated_at_utc: str
    build_number: int | None
    expected_dataset_count: int
    present_dataset_count: int
    missing_dataset_count: int
    extra_files: list[str]
    network_warnings: list[str]
    datasets: dict[str, DatasetValidationResult]


@dataclass
class EnhancedValidationResults:
    """Structured validation results for YAML/JSONL SDE datasets.

    This class encapsulates all relevant information about the validation process,
    including dataset details, timing metrics, and any encountered errors or warnings.
    """

    source_format: Literal["yaml-model", "jsonl-model"]
    source_media: Literal["file", "db"]
    sde_metadata: SdeMetadata
    schema_report: Any
    schema_report_markdown: str
    schema_changes: str | None
    data_changes: str | None
    sde_validation_summary: SdeValidationSummary
    sde_validation_markdown_report: str


class DatasetInput(TypedDict):
    """Input tuple for one normalized dataset."""

    dataset_name: str
    dataset_data: dict[int | str, Any]
    sde_metadata: SdeMetadata
