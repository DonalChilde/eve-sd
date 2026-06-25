"""Markdown rendering for SDE validation summaries."""

from eve_static_data.validation.models import (
    DatasetValidationResult,
    FailedRecordValidation,
    SdeValidationSummary,
)


def generate_markdown_report(sde_validation_summary: SdeValidationSummary) -> str:
    """Generate a deterministic markdown report for SDE validation results.

    Args:
        sde_validation_summary: Full validation summary for an SDE source.

    Returns:
        A human-readable markdown report.
    """
    total_records = _total_records(sde_validation_summary.validation_results)
    total_failed_records = _total_failed_records(
        sde_validation_summary.validation_results
    )
    duration_nanos = (
        sde_validation_summary.finished_timestamp_nanos
        - sde_validation_summary.started_timestamp_nanos
    )

    lines: list[str] = [
        "# SDE Validation Report",
        "",
        "## Summary",
        f"- build_number: {sde_validation_summary.sde_metadata.buildNumber}",
        f"- release_date: {sde_validation_summary.sde_metadata.releaseDate}",
        f"- source_format: {sde_validation_summary.sde_metadata.source_format}",
        f"- source_media: {sde_validation_summary.sde_metadata.source_media}",
        f"- started_timestamp_nanos: {sde_validation_summary.started_timestamp_nanos}",
        f"- finished_timestamp_nanos: {sde_validation_summary.finished_timestamp_nanos}",
        f"- duration: {_format_duration_nanos(duration_nanos)}",
        f"- total_records: {total_records}",
        f"- total_failed_records: {total_failed_records}",
        (f"- pass_rate: {_format_pass_rate(total_failed_records, total_records)}"),
        "",
        "## Dataset Coverage",
        f"- expected_datasets: {sde_validation_summary.expected_datasets}",
        f"- validated_datasets: {sde_validation_summary.validated_datasets}",
        f"- missing_dataset_count: {len(sde_validation_summary.missing_datasets)}",
        (
            "- unexpected_dataset_count: "
            f"{len(sde_validation_summary.unexpected_datasets)}"
        ),
        "",
        "### Missing Datasets",
        "",
    ]

    missing_datasets = sorted(sde_validation_summary.missing_datasets)
    if missing_datasets:
        lines.extend(f"- {dataset_name}" for dataset_name in missing_datasets)
    else:
        lines.append("- None")

    lines.extend(["", "### Unexpected Datasets", ""])
    unexpected_datasets = sorted(sde_validation_summary.unexpected_datasets)
    if unexpected_datasets:
        lines.extend(f"- {dataset_name}" for dataset_name in unexpected_datasets)
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "## Dataset Results",
            "",
            "| Dataset | Records | Failed | Valid | Validation Time |",
            "|---------|---------|--------|-------|-----------------|",
        ]
    )

    for dataset_name, result in _sorted_results(
        sde_validation_summary.validation_results
    ):
        lines.append(
            "| "
            f"{dataset_name} | "
            f"{result.record_count} | "
            f"{len(result.failed_records)} | "
            f"{'yes' if result.is_valid() else 'no'} | "
            f"{_format_optional_duration_nanos(result.validation_time_nanoseconds)} |"
        )

    lines.extend(["", "## Validation Failures", ""])

    has_failures = False
    for dataset_name, result in _sorted_results(
        sde_validation_summary.validation_results
    ):
        if result.is_valid():
            continue
        has_failures = True
        lines.append(f"### {dataset_name}")
        lines.append("")
        for failed_record in result.failed_records:
            lines.extend(_render_failed_record(failed_record))
        lines.append("")

    if not has_failures:
        lines.append("No validation failures detected.")

    return "\n".join(lines).rstrip() + "\n"


def _sorted_results(
    validation_results: dict[str, DatasetValidationResult],
) -> list[tuple[str, DatasetValidationResult]]:
    """Return validation results sorted by dataset name."""
    return sorted(validation_results.items(), key=lambda item: item[0])


def _total_records(validation_results: dict[str, DatasetValidationResult]) -> int:
    """Return total number of validated records across all datasets."""
    return sum(result.record_count for result in validation_results.values())


def _total_failed_records(
    validation_results: dict[str, DatasetValidationResult],
) -> int:
    """Return total number of failed records across all datasets."""
    return sum(len(result.failed_records) for result in validation_results.values())


def _format_duration_nanos(duration_nanos: int) -> str:
    """Format a nanosecond duration into seconds with millisecond precision."""
    return f"{duration_nanos / 1_000_000_000:.3f} seconds"


def _format_optional_duration_nanos(duration_nanos: int | None) -> str:
    """Format an optional nanosecond duration for markdown output."""
    if duration_nanos is None:
        return "n/a"
    return _format_duration_nanos(duration_nanos)


def _format_pass_rate(total_failed_records: int, total_records: int) -> str:
    """Format pass rate as a percentage string.

    Args:
        total_failed_records: Total failed records across all datasets.
        total_records: Total validated records across all datasets.

    Returns:
        Pass rate percent string, or ``n/a`` when there are no records.
    """
    if total_records == 0:
        return "n/a"
    passed_records = total_records - total_failed_records
    return f"{(passed_records / total_records) * 100:.2f}%"


def _render_failed_record(failed_record: FailedRecordValidation) -> list[str]:
    """Render one failed record and its error messages as markdown lines."""
    lines = [f"- key={failed_record.top_level_key}"]
    lines.extend(f"  - {message}" for message in failed_record.error_messages)
    return lines
