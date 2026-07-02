"""Tests for validation markdown report rendering."""

from eve_sd.models.dataset_filenames import SdeDatasets
from eve_sd.validation.markdown_report import generate_markdown_report
from eve_sd.validation.models import (
    DatasetValidationResult,
    FailedRecordValidation,
    SdeValidationSummary,
)

from eve_sd.helpers.sde_metadata import SdeMetadata, SdeVariant, SourceMedia


def _metadata() -> SdeMetadata:
    """Build sample SDE metadata for report tests."""
    return SdeMetadata(
        buildNumber=3393779,
        releaseDate="2026-06-14T11:47:47Z",
        variant=SdeVariant.YAML,
        source_media=SourceMedia.YAML,
    )


def _result(
    dataset: SdeDatasets,
    record_count: int,
    validation_time_nanoseconds: int | None,
    failed_records: list[FailedRecordValidation],
) -> DatasetValidationResult:
    """Build one dataset result for report tests."""
    return DatasetValidationResult(
        dataset=dataset,
        source_format=SdeVariant.YAML,
        record_count=record_count,
        validation_time_nanoseconds=validation_time_nanoseconds,
        failed_records=failed_records,
    )


def test_generate_markdown_report_includes_summary_and_dataset_table() -> None:
    """Report should include summary, coverage, and dataset table values."""
    summary = SdeValidationSummary(
        sde_metadata=_metadata(),
        started_timestamp_nanos=1_000_000_000,
        finished_timestamp_nanos=3_500_000_000,
        expected_datasets=60,
        validated_datasets=2,
        missing_datasets={"agentsInSpace"},
        unexpected_datasets={"surpriseDataset"},
        validation_results={
            "types": _result(SdeDatasets.TYPES, 4, 500_000_000, []),
            "blueprints": _result(SdeDatasets.BLUEPRINTS, 6, None, []),
        },
    )

    markdown = generate_markdown_report(summary)

    assert "# SDE Validation Report" in markdown
    assert "## Summary" in markdown
    assert "- build_number: 3393779" in markdown
    assert "- duration: 2.500 seconds" in markdown
    assert "- total_records: 10" in markdown
    assert "- total_failed_records: 0" in markdown
    assert "- pass_rate: 100.00%" in markdown
    assert "## Dataset Coverage" in markdown
    assert "- expected_datasets: 60" in markdown
    assert "- validated_datasets: 2" in markdown
    assert "### Missing Datasets" in markdown
    assert "- agentsInSpace" in markdown
    assert "### Unexpected Datasets" in markdown
    assert "- surpriseDataset" in markdown
    assert "| Dataset | Records | Failed | Valid | Validation Time |" in markdown
    assert "| blueprints | 6 | 0 | yes | n/a |" in markdown
    assert "| types | 4 | 0 | yes | 0.500 seconds |" in markdown
    assert markdown.endswith("\n")


def test_generate_markdown_report_renders_all_failed_records_and_messages() -> None:
    """Report should include every failed record and all error messages."""
    failed_records = [
        FailedRecordValidation(
            dataset="types",
            top_level_key=34,
            error_messages=[
                "name.en: field required",
                "mass: Input should be greater than 0",
            ],
        ),
        FailedRecordValidation(
            dataset="types",
            top_level_key=35,
            error_messages=["groupID: Input should be a valid integer"],
        ),
    ]
    summary = SdeValidationSummary(
        sde_metadata=_metadata(),
        started_timestamp_nanos=1,
        finished_timestamp_nanos=10,
        expected_datasets=60,
        validated_datasets=1,
        missing_datasets=set(),
        unexpected_datasets=set(),
        validation_results={
            "types": _result(SdeDatasets.TYPES, 2, 2_000_000, failed_records),
        },
    )

    markdown = generate_markdown_report(summary)

    assert "## Validation Failures" in markdown
    assert "### types" in markdown
    assert "- key=34" in markdown
    assert "  - name.en: field required" in markdown
    assert "  - mass: Input should be greater than 0" in markdown
    assert "- key=35" in markdown
    assert "  - groupID: Input should be a valid integer" in markdown
    assert "No validation failures detected." not in markdown


def test_generate_markdown_report_sorts_datasets_and_empty_coverage_sections() -> None:
    """Dataset rows should be deterministic and empty coverage should render None."""
    summary = SdeValidationSummary(
        sde_metadata=_metadata(),
        started_timestamp_nanos=1,
        finished_timestamp_nanos=1,
        expected_datasets=60,
        validated_datasets=3,
        missing_datasets=set(),
        unexpected_datasets=set(),
        validation_results={
            "types": _result(SdeDatasets.TYPES, 1, 1_000, []),
            "ancestries": _result(SdeDatasets.ANCESTRIES, 1, 1_000, []),
            "blueprints": _result(SdeDatasets.BLUEPRINTS, 1, 1_000, []),
        },
    )

    markdown = generate_markdown_report(summary)

    ancestries_index = markdown.index("| ancestries |")
    blueprints_index = markdown.index("| blueprints |")
    types_index = markdown.index("| types |")

    assert ancestries_index < blueprints_index < types_index
    assert "### Missing Datasets\n\n- None" in markdown
    assert "### Unexpected Datasets\n\n- None" in markdown
    assert "No validation failures detected." in markdown
