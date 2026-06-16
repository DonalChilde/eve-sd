"""Validation workflow for YAML/JSON SDE datasets.

This module validates each dataset file represented by ``SdeDatasetFiles`` against
its corresponding pydantic ``RootModel`` from ``yaml_datasets``. Validation outputs
include machine-readable JSON results, a markdown report, schema inspection reports,
and optional network artifacts (schema changelog and data changes) for the detected
build number.
"""
# TODO Refactor to support yaml datasets from files, as well as from db.
# - use the custom safeload function when loading from file to take advantage of the CSafeLoader if available.
# - collect all the reports, and downloads into one class that can be passed around afterwards.
#   - This will make it easy to persist the reports in multiple formats, and also to use the network artifacts in other contexts if needed.
# - The validate files and validate from db should come up with largely the same results, and the same report format, so that we can easily compare the results from both sources.
# - It looks like the validation logic should be simplified

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter
from typing import Any, Literal, cast

from pydantic import RootModel, ValidationError
from yaml import YAMLError, safe_load

from eve_static_data.helpers import schema_report
from eve_static_data.helpers.save_text_file import save_text_file
from eve_static_data.models import yaml_datasets
from eve_static_data.models.dataset_filenames import SdeDatasetFiles
from eve_static_data.sde_tools import SDETools

logger = logging.getLogger(__name__)

type RootModelType = type[RootModel[Any]]
type DatasetFileResolution = tuple[Path, str]


def _failed_record_list() -> list[FailedRecordValidation]:
    """Return a typed default list for failed record entries."""
    return []


@dataclass
class EnhancedValidationResults:
    """Structured validation results for YAML/JSON SDE datasets.

    This class encapsulates all relevant information about the validation process,
    including dataset details, timing metrics, and any encountered errors or warnings.
    """

    source_format: Literal["yaml", "json"]
    source_media: Literal["file", "db"]
    sde_metadata: Any  # use helper function.
    schema_report: Any
    schema_report_markdown: str
    schema_changes: str | None
    data_changes: str | None
    yaml_validation_summary: YamlValidationSummary
    yaml_validation_markdown_report: str


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
        file_name: Expected base file name from ``SdeDatasetFiles``.
        file_path: Resolved file path if found.
        file_flavor: Source flavor selected for validation.
        file_size_bytes: Source file size in bytes.
        record_count: Number of top-level records.
        load_time_seconds: Elapsed load time measured by ``perf_counter``.
        validation_time_seconds: Elapsed validation time measured by
            ``perf_counter``.
        missing_file: Whether no supported source file was found.
        parse_error: Parsing or shape error string if encountered.
        failed_records: Per-record validation errors.
    """

    dataset: str
    file_name: str
    file_path: str | None = None
    file_flavor: str | None = None
    file_size_bytes: int | None = None
    record_count: int = 0
    load_time_seconds: float | None = None
    validation_time_seconds: float | None = None
    missing_file: bool = False
    parse_error: str | None = None
    failed_records: list[FailedRecordValidation] = field(
        default_factory=_failed_record_list
    )

    def is_valid(self) -> bool:
        """Return ``True`` when dataset validation has no errors."""
        return (
            not self.missing_file
            and self.parse_error is None
            and len(self.failed_records) == 0
        )


@dataclass
class YamlValidationSummary:
    """Complete validation result payload for an SDE directory."""

    sde_path: str
    output_path: str
    generated_at_utc: str
    build_number: int | None
    expected_dataset_count: int
    present_dataset_count: int
    missing_dataset_count: int
    extra_files: list[str]
    network_warnings: list[str]
    datasets: dict[str, DatasetValidationResult]


def _dataset_candidates(dataset: SdeDatasetFiles) -> list[tuple[str, str]]:
    """Return preferred file candidates and flavor names for a dataset.

    Args:
        dataset: Dataset enum value.

    Returns:
        Ordered list of ``(file_name, flavor)`` candidates.
    """
    yaml_name = dataset.as_yaml()
    yml_name = yaml_name.removesuffix(".yaml") + ".yml"
    return [
        (dataset.as_json(), "json"),
        (yaml_name, "yaml"),
        (yml_name, "yml"),
    ]


def _resolve_dataset_file(
    sde_path: Path, dataset: SdeDatasetFiles
) -> DatasetFileResolution | None:
    """Resolve the first available source file for a dataset.

    Args:
        sde_path: Directory containing SDE source datasets.
        dataset: Dataset enum value.

    Returns:
        Path and flavor for the selected source file, or ``None`` if missing.
    """
    for file_name, flavor in _dataset_candidates(dataset):
        file_path = sde_path / file_name
        if file_path.is_file():
            return file_path, flavor
    return None


def _expected_candidate_names() -> set[str]:
    """Return all accepted dataset file names across all supported flavors."""
    names: set[str] = set()
    for dataset in SdeDatasetFiles:
        for file_name, _ in _dataset_candidates(dataset):
            names.add(file_name)
    return names


def _load_dataset_mapping(
    file_path: Path,
) -> tuple[dict[str, object] | None, str | None]:
    """Load a JSON/YAML dataset file and enforce dict shape.

    Args:
        file_path: Source dataset file path.

    Returns:
        A tuple of ``(mapping, error_message)``.
    """
    try:
        with file_path.open(encoding="utf-8") as source:
            if file_path.suffix == ".json":
                payload: object = json.load(source)
            elif file_path.suffix in {".yaml", ".yml"}:
                payload = safe_load(source)
            else:
                return None, f"Unsupported dataset suffix: {file_path.suffix}"
    except (OSError, json.JSONDecodeError, YAMLError) as exc:
        return None, str(exc)

    if not isinstance(payload, dict):
        return None, "Dataset payload must be a top-level dict."

    mapping = cast(dict[object, object], payload)
    return {str(key): value for key, value in mapping.items()}, None


def _validation_error_messages(exc: ValidationError) -> list[str]:
    """Normalize pydantic validation errors into readable messages.

    Args:
        exc: Pydantic ``ValidationError`` instance.

    Returns:
        List of normalized error strings.
    """
    messages: list[str] = []
    for error in exc.errors():
        location = ".".join(str(value) for value in error.get("loc", []))
        message = str(error.get("msg", "Validation error"))
        if location:
            messages.append(f"{location}: {message}")
        else:
            messages.append(message)
    if not messages:
        return [str(exc)]
    return messages


def _extract_build_number(payload: dict[str, object] | None) -> int | None:
    """Extract ``buildNumber`` from the ``_sde`` dataset payload.

    Args:
        payload: Parsed top-level mapping for ``_sde``.

    Returns:
        Build number if available and valid.
    """
    if payload is None:
        return None
    sde_record = payload.get("sde")
    if not isinstance(sde_record, dict):
        return None
    typed_sde_record = cast(dict[str, object], sde_record)
    build_number = typed_sde_record.get("buildNumber")
    if isinstance(build_number, int):
        return build_number
    return None


def _format_seconds(duration: float | None) -> str:
    """Return a report-safe seconds string with 3 decimal places."""
    if duration is None:
        return "n/a"
    return f"{duration:.3f} seconds"


def _render_markdown_report(summary: YamlValidationSummary) -> str:
    """Render a markdown report for YAML dataset validation results.

    Args:
        summary: Validation summary payload.

    Returns:
        Markdown text report.
    """
    lines: list[str] = [
        "# YAML Dataset Validation Report",
        "",
        "## Summary",
        f"- sde_path: {summary.sde_path}",
        f"- output_path: {summary.output_path}",
        f"- generated_at_utc: {summary.generated_at_utc}",
        (
            "- build_number: "
            f"{summary.build_number if summary.build_number is not None else 'unknown'}"
        ),
        f"- expected_dataset_count: {summary.expected_dataset_count}",
        f"- present_dataset_count: {summary.present_dataset_count}",
        f"- missing_dataset_count: {summary.missing_dataset_count}",
        f"- extra_file_count: {len(summary.extra_files)}",
        "",
    ]

    if summary.extra_files:
        lines.append("### Extra Files")
        lines.append("")
        lines.extend(f"- {name}" for name in summary.extra_files)
        lines.append("")

    if summary.network_warnings:
        lines.append("### Network Warnings")
        lines.append("")
        lines.extend(f"- {warning}" for warning in summary.network_warnings)
        lines.append("")

    lines.extend(
        [
            "## Dataset Results",
            "",
            (
                "| Dataset | File | Flavor | Size (bytes) | "
                "Records | Load Time | Validation Time | Valid |"
            ),
            (
                "|---------|------|--------|--------------|---------|-----------"
                "|-----------------|-------|"
            ),
        ]
    )

    for dataset_name in sorted(summary.datasets):
        result = summary.datasets[dataset_name]
        lines.append(
            "| "
            f"{dataset_name} | "
            f"{result.file_path or result.file_name} | "
            f"{result.file_flavor or 'missing'} | "
            f"{result.file_size_bytes if result.file_size_bytes is not None else 'n/a'} | "
            f"{result.record_count} | "
            f"{_format_seconds(result.load_time_seconds)} | "
            f"{_format_seconds(result.validation_time_seconds)} | "
            f"{'yes' if result.is_valid() else 'no'} |"
        )

    lines.append("")
    lines.append("## Failures")
    lines.append("")

    has_failures = False
    for dataset_name in sorted(summary.datasets):
        result = summary.datasets[dataset_name]
        if result.is_valid():
            continue
        has_failures = True
        lines.append(f"### {dataset_name}")
        lines.append("")
        if result.missing_file:
            lines.append("- Missing dataset source file.")
        if result.parse_error is not None:
            lines.append(f"- Parse error: {result.parse_error}")
        for failed_record in result.failed_records:
            lines.append(f"- key={failed_record.top_level_key}")
            for message in failed_record.error_messages:
                lines.append(f"  - {message}")
        lines.append("")

    if not has_failures:
        lines.append("No validation failures detected.")

    return "\n".join(lines).rstrip() + "\n"


async def _save_network_artifacts(
    build_number: int | None,
    output_path: Path,
    sde_tools: SDETools,
    overwrite: bool,
) -> list[str]:
    """Fetch and persist optional network artifacts for the validated build.

    Args:
        build_number: Build number extracted from ``_sde`` dataset.
        output_path: Directory to save downloaded artifacts.
        sde_tools: SDE tools network client.
        overwrite: Whether to overwrite existing output files.

    Returns:
        Warning strings for non-fatal failures.
    """
    warnings: list[str] = []
    if build_number is None:
        warnings.append("Skipped network artifact downloads: build number unavailable.")
        return warnings

    try:
        schema_changelog = await sde_tools.fetch_schema_changelog(build_number)
        save_text_file(
            text=schema_changelog,
            output_path=output_path,
            file_name=f"schema_changelog_{build_number}.yaml",
            overwrite=overwrite,
        )
    except Exception as exc:  # pragma: no cover - defensive network error capture.
        warnings.append(f"Failed to fetch schema changelog: {exc}")

    try:
        data_changes = await sde_tools.fetch_data_changes(build_number)
        save_text_file(
            text=data_changes,
            output_path=output_path,
            file_name=f"data_changes_{build_number}.jsonl",
            overwrite=overwrite,
        )
    except Exception as exc:  # pragma: no cover - defensive network error capture.
        warnings.append(f"Failed to fetch data changes: {exc}")

    return warnings


async def validate_yaml_datasets(
    sde_path: Path,
    output_path: Path | None = None,
    sde_tools: SDETools | None = None,
    overwrite: bool = True,
) -> dict[str, Any]:
    """Validate all YAML/JSON datasets under an SDE directory.

    Args:
        sde_path: Path to a directory containing dataset source files.
        output_path: Optional report output directory. Defaults to
            ``<sde_path>/validation_results``.
        sde_tools: Optional ``SDETools`` instance for network artifact downloads.
        overwrite: Whether existing report files may be overwritten.

    Returns:
        Dictionary containing complete validation results.

    Raises:
        FileNotFoundError: If ``sde_path`` does not exist.
        NotADirectoryError: If ``sde_path`` is not a directory.
    """
    if not sde_path.exists():
        raise FileNotFoundError(f"SDE path does not exist: {sde_path}")
    if not sde_path.is_dir():
        raise NotADirectoryError(f"SDE path is not a directory: {sde_path}")

    resolved_output_path = output_path or (sde_path / "validation_results")
    resolved_output_path.mkdir(parents=True, exist_ok=True)

    root_model_lookup = yaml_datasets.files_to_root_model_lookup()
    dataset_results: dict[str, DatasetValidationResult] = {}
    build_number: int | None = None

    for dataset in SdeDatasetFiles:
        result = DatasetValidationResult(dataset=dataset.name, file_name=dataset.value)
        root_model: RootModelType = root_model_lookup[dataset]
        resolved = _resolve_dataset_file(sde_path, dataset)
        if resolved is None:
            result.missing_file = True
            dataset_results[dataset.name] = result
            continue

        file_path, flavor = resolved
        result.file_path = str(file_path)
        result.file_flavor = flavor
        result.file_size_bytes = file_path.stat().st_size

        load_start = perf_counter()
        payload, payload_error = _load_dataset_mapping(file_path)
        result.load_time_seconds = perf_counter() - load_start
        if payload_error is not None:
            result.parse_error = payload_error
            dataset_results[dataset.name] = result
            continue

        assert payload is not None
        result.record_count = len(payload)

        validate_start = perf_counter()
        for top_level_key, record_payload in payload.items():
            try:
                root_model.model_validate(
                    {top_level_key: record_payload}, extra="forbid"
                )
            except ValidationError as exc:
                result.failed_records.append(
                    FailedRecordValidation(
                        dataset=dataset.name,
                        top_level_key=str(top_level_key),
                        error_messages=_validation_error_messages(exc),
                    )
                )
        result.validation_time_seconds = perf_counter() - validate_start

        if dataset == SdeDatasetFiles.SDE_INFO:
            build_number = _extract_build_number(payload)

        dataset_results[dataset.name] = result

    expected_names = _expected_candidate_names()
    present_files = {
        path.name
        for path in sde_path.iterdir()
        if path.is_file() and path.suffix in {".json", ".yaml", ".yml"}
    }
    extra_files = sorted(present_files - expected_names)

    summary = YamlValidationSummary(
        sde_path=str(sde_path),
        output_path=str(resolved_output_path),
        generated_at_utc=datetime.now(UTC).isoformat(timespec="seconds"),
        build_number=build_number,
        expected_dataset_count=len(SdeDatasetFiles),
        present_dataset_count=sum(
            1 for result in dataset_results.values() if not result.missing_file
        ),
        missing_dataset_count=sum(
            1 for result in dataset_results.values() if result.missing_file
        ),
        extra_files=extra_files,
        network_warnings=[],
        datasets=dataset_results,
    )

    # Save validation outputs first so local analysis is available even if network
    # artifact downloads fail.
    summary_dict = asdict(summary)
    markdown_report = _render_markdown_report(summary)
    file_suffix = str(build_number) if build_number is not None else "unknown"
    save_text_file(
        text=json.dumps(summary_dict, indent=2),
        output_path=resolved_output_path,
        file_name=f"yaml_validation_result_{file_suffix}.json",
        overwrite=overwrite,
    )
    save_text_file(
        text=markdown_report,
        output_path=resolved_output_path,
        file_name=f"yaml_validation_report_{file_suffix}.md",
        overwrite=overwrite,
    )

    schema_report_data = schema_report.scan_directory(sde_path, sde_format="yaml-model")
    save_text_file(
        text=json.dumps(schema_report_data, indent=2),
        output_path=resolved_output_path,
        file_name="yaml_schema_report.json",
        overwrite=overwrite,
    )
    save_text_file(
        text=schema_report.generate_markdown_report(schema_report_data),
        output_path=resolved_output_path,
        file_name="yaml_schema_report.md",
        overwrite=overwrite,
    )

    network_client = sde_tools or SDETools()
    summary.network_warnings = await _save_network_artifacts(
        build_number=build_number,
        output_path=resolved_output_path,
        sde_tools=network_client,
        overwrite=overwrite,
    )
    if summary.network_warnings:
        logger.warning("YAML validation network warnings: %s", summary.network_warnings)

    # Persist once more to include network warnings captured after downloads.
    summary_dict = asdict(summary)
    save_text_file(
        text=json.dumps(summary_dict, indent=2),
        output_path=resolved_output_path,
        file_name=f"yaml_validation_result_{file_suffix}.json",
        overwrite=True,
    )

    return summary_dict
