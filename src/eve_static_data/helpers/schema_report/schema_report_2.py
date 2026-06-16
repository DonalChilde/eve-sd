"""Generate schema inspection reports for SDE datasets.

Supports two SDE source formats:

- ``"yaml-model"``: top-level value is a ``dict`` mapping record IDs to record
  dicts (produced from YAML or yaml-converted-to-JSON datasets).  Nested dicts
  whose keys are integers (or digit-only strings from JSON conversion) are
  automatically normalised to the sentinel path component ``INTEGER_KEY`` to
  avoid path explosion.

- ``"jsonl-model"``: top-level value is a ``list`` of record dicts, where each
  record carries a ``_key`` field identifying the record.  Integer key
  normalisation is **not** applied for this format because field names in JSON
  are always strings and the ``_key`` field is a first-class schema member.
"""
# TODO Refactor to support yaml datasets from files, as well as from db.
# - use the custom safeload function when loading from file to take advantage of the CSafeLoader if available.
# - load datasets from various sources, then pass the loaded data to a common inspection function that doesn't need to know about the source format.
# - resulting loaded data should be a dict[str | int, Any] for yaml-model and jsonl-model, so the inspection function can be shared with minimal branching.
# - need function for loading jsonl files as dict[str|int,Any]

from __future__ import annotations

import logging
from collections import Counter
from dataclasses import dataclass, field
from datetime import UTC, datetime
from glob import glob
from pathlib import Path
from typing import Any, Literal, TypedDict, cast

from yaml import YAMLError

from eve_static_data.helpers import json_io
from eve_static_data.helpers.yaml_loader import safe_load_path

logger = logging.getLogger(__name__)

type PathStatsMap = dict[str, "PathInspection"]
type DatasetMap = dict[str, "DatasetInspection"]
type WarningList = list[str]

SdeTypeName = Literal["dict", "list", "str", "int", "float", "bool", "null"]
SdeFormat = Literal["yaml-model", "jsonl-model"]
ValidSuffixes: dict[SdeFormat, set[str]] = {
    "yaml-model": {".yaml", ".yml", ".json"},
    "jsonl-model": {".json"},
}

#: Sentinel path component used in place of integer keys for ``yaml-model`` datasets.
INTEGER_KEY = "INTEGER_KEY"


def _string_counter() -> Counter[str]:
    """Return a typed string counter for dataclass defaults."""
    return Counter()


def _field_node_map() -> dict[str, _FieldNode]:
    """Return a typed field-node mapping for dataclass defaults."""
    return {}


class PathInspection(TypedDict):
    """Flattened inspection data for one dotted field path."""

    path: str
    presence_count: int
    container_count: int
    required: bool
    value_type_counts: dict[str, int]


class DatasetInspection(TypedDict):
    """Inspection output for one dataset file."""

    file_name: str
    file_path: str
    sde_format: SdeFormat
    top_level_key_type_counts: dict[str, int]
    total_records: int
    valid_record_count: int
    skipped_record_count: int
    path_count: int
    paths: PathStatsMap
    warnings: WarningList


class SchemaReport(TypedDict):
    """Top-level schema report for one or more dataset files."""

    source_path: str
    generated_at_utc: str
    sde_format: SdeFormat
    file_count: int
    total_records: int
    total_unique_paths: int
    datasets: DatasetMap


@dataclass
class _ListStats:
    """Mutable aggregation state for list-valued paths."""

    item_count: int = 0
    item_type_counts: Counter[str] = field(default_factory=_string_counter)
    empty_list_count: int = 0
    item_node: _FieldNode = field(default_factory=lambda: _FieldNode())


@dataclass
class _FieldNode:
    """Mutable aggregation node for one observed path."""

    presence_count: int = 0
    value_type_counts: Counter[str] = field(default_factory=_string_counter)
    children: dict[str, _FieldNode] = field(default_factory=_field_node_map)
    list_stats: _ListStats | None = None


def _sde_type_name(value: Any) -> SdeTypeName:
    """Return a normalised SDE value type name.

    Args:
        value: Parsed value from a YAML or JSON dataset.

    Returns:
        Stable type label used in reports.
    """
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, str):
        return "str"
    if isinstance(value, list):
        return "list"
    return "dict"


def _mapping_items(value: Any) -> list[tuple[object, object]]:
    """Return mapping items with a concrete type for iteration."""
    return list(cast(dict[object, object], value).items())


def _sequence_items(value: Any) -> list[object]:
    """Return sequence items with a concrete type for iteration."""
    return list(cast(list[object], value))


def _normalize_child_key(key: object, sde_format: SdeFormat) -> str:
    """Return the path component for a child dict key.

    For ``yaml-model`` datasets, integer keys and digit-only string keys
    (which arise when a YAML file with integer keys is converted to JSON) are
    replaced with the sentinel ``INTEGER_KEY`` to collapse structurally
    identical sibling paths.

    Args:
        key: Child key observed in the source data.
        sde_format: Active source format for this scan.

    Returns:
        Normalised path component string.

    Examples:
        >>> _normalize_child_key(3380, "yaml-model")
        'INTEGER_KEY'
        >>> _normalize_child_key("3380", "yaml-model")
        'INTEGER_KEY'
        >>> _normalize_child_key("name", "yaml-model")
        'name'
        >>> _normalize_child_key("3380", "jsonl-model")
        '3380'
    """
    if sde_format == "yaml-model":
        if isinstance(key, int):
            return INTEGER_KEY
        str_key = str(key)
        if str_key.lstrip("-").isdigit():
            return INTEGER_KEY
    return str(key)


def _update_node_from_value(
    node: _FieldNode, value: Any, sde_format: SdeFormat
) -> None:
    """Recursively aggregate one observed value into a field node.

    Args:
        node: Aggregation node to update.
        value: Observed value for the path represented by ``node``.
        sde_format: Active source format controlling key normalisation.
    """
    type_name = _sde_type_name(value)
    node.value_type_counts[type_name] += 1

    if isinstance(value, dict):
        for child_name, child_value in _mapping_items(value):
            child_key = _normalize_child_key(child_name, sde_format)
            child_node = node.children.setdefault(child_key, _FieldNode())
            child_node.presence_count += 1
            _update_node_from_value(child_node, child_value, sde_format)
        return

    if not isinstance(value, list):
        return

    list_stats = node.list_stats
    if list_stats is None:
        list_stats = _ListStats()
        node.list_stats = list_stats

    if not value:
        list_stats.empty_list_count += 1
        return

    for item in _sequence_items(value):
        item_type = _sde_type_name(item)
        list_stats.item_count += 1
        list_stats.item_type_counts[item_type] += 1
        if isinstance(item, dict):
            list_stats.item_node.presence_count += 1
            _update_node_from_value(list_stats.item_node, item, sde_format)


def _sorted_type_counts(type_counts: dict[str, int]) -> dict[str, int]:
    """Return type counts in a stable display order.

    Args:
        type_counts: Raw type counter mapping.

    Returns:
        Ordered dictionary preserving deterministic output.
    """
    keys = sorted(type_counts)
    return {key: type_counts[key] for key in keys}


def _flatten_field_rows(
    fields: dict[str, _FieldNode],
    container_count: int,
    prefix: str = "",
    ancestor_required: bool = True,
) -> PathStatsMap:
    """Flatten recursive field nodes into dotted-path rows.

    Args:
        fields: Field nodes for the current object level.
        container_count: Number of parent containers at this level.
        prefix: Current dotted-path prefix.
        ancestor_required: Whether every ancestor path is required.

    Returns:
        Flat mapping of dotted paths to report rows.
    """
    rows: PathStatsMap = {}

    for field_name in sorted(fields):
        field_data = fields[field_name]
        path = f"{prefix}.{field_name}" if prefix else field_name
        local_required = (
            container_count > 0 and field_data.presence_count >= container_count
        )
        required = ancestor_required and local_required
        rows[path] = {
            "path": path,
            "presence_count": field_data.presence_count,
            "container_count": container_count,
            "required": required,
            "value_type_counts": _sorted_type_counts(
                dict(field_data.value_type_counts)
            ),
        }

        dict_count = field_data.value_type_counts.get("dict", 0)
        if field_data.children and dict_count:
            rows.update(
                _flatten_field_rows(
                    fields=field_data.children,
                    container_count=dict_count,
                    prefix=path,
                    ancestor_required=required,
                )
            )

        list_stats = field_data.list_stats
        list_dict_count = 0
        if list_stats is not None:
            list_dict_count = list_stats.item_type_counts.get("dict", 0)

        if list_stats is not None and list_stats.item_node.children and list_dict_count:
            rows.update(
                _flatten_field_rows(
                    fields=list_stats.item_node.children,
                    container_count=list_dict_count,
                    prefix=path,
                    ancestor_required=required,
                )
            )

    return rows


def _append_warning(warnings: WarningList, message: str) -> None:
    """Append a warning if it has not been recorded yet.

    Args:
        warnings: Accumulated warning messages.
        message: Warning text to add.
    """
    if message not in warnings:
        warnings.append(message)


def _collect_node_warnings(
    path: str,
    node: _FieldNode,
    warnings: WarningList,
) -> None:
    """Collect warnings from a field node and its descendants.

    Args:
        path: Dotted path represented by ``node``.
        node: Field node to inspect.
        warnings: Mutable warning list to update.
    """
    container_types = {"dict", "list"}
    scalar_types = set(node.value_type_counts) - container_types
    if container_types & set(node.value_type_counts) and scalar_types:
        type_summary = ", ".join(
            f"{name}:{count}"
            for name, count in _sorted_type_counts(dict(node.value_type_counts)).items()
        )
        _append_warning(
            warnings,
            f"{path}: path mixes container and scalar types ({type_summary})",
        )

    list_stats = node.list_stats
    if list_stats is not None:
        if list_stats.empty_list_count:
            suffix = "s" if list_stats.empty_list_count != 1 else ""
            _append_warning(
                warnings,
                f"{path}: encountered {list_stats.empty_list_count} empty list{suffix}",
            )
        if len(list_stats.item_type_counts) > 1:
            item_summary = ", ".join(
                f"{name}:{count}"
                for name, count in _sorted_type_counts(
                    dict(list_stats.item_type_counts)
                ).items()
            )
            _append_warning(
                warnings,
                f"{path}: list contains mixed item types ({item_summary})",
            )

    for child_name in sorted(node.children):
        child_path = f"{path}.{child_name}" if path else child_name
        _collect_node_warnings(child_path, node.children[child_name], warnings)

    if list_stats is None:
        return

    for child_name in sorted(list_stats.item_node.children):
        child_path = f"{path}.{child_name}" if path else child_name
        _collect_node_warnings(
            child_path, list_stats.item_node.children[child_name], warnings
        )


def _inspect_dataset(file_path: Path, sde_format: SdeFormat) -> DatasetInspection:
    """Inspect one dataset file.

    Args:
        file_path: Dataset file to inspect (JSON, YAML, or YML).
        sde_format: Expected top-level structure of the dataset.

    Returns:
        Flattened inspection report for a single dataset file.
    """
    warnings: WarningList = []
    root_fields: dict[str, _FieldNode] = {}
    top_level_key_type_counts: Counter[str] = _string_counter()

    def _empty_result(extra_warnings: list[str]) -> DatasetInspection:
        return {
            "file_name": file_path.name,
            "file_path": str(file_path),
            "sde_format": sde_format,
            "top_level_key_type_counts": {},
            "total_records": 0,
            "valid_record_count": 0,
            "skipped_record_count": 0,
            "path_count": 0,
            "paths": {},
            "warnings": extra_warnings,
        }

    try:
        if file_path.suffix.lower() == ".json":
            data = json_io.json_load_path(file_path)
        elif file_path.suffix.lower() in {".yaml", ".yml"}:
            data = safe_load_path(file_path)
        else:
            _append_warning(
                warnings,
                f"Unrecognised file extension {file_path.suffix}; "
                "attempting to parse as YAML",
            )
            data = safe_load_path(file_path)
    except (YAMLError, ValueError) as exc:
        logger.warning("Failed to parse dataset file %s: %s", file_path, exc)
        return _empty_result([f"Failed to parse file: {exc}"])

    total_records = 0
    valid_record_count = 0
    skipped_record_count = 0

    if sde_format == "yaml-model":
        if not isinstance(data, dict):
            type_name = _sde_type_name(data)
            return _empty_result(
                [
                    f"yaml-model expects a top-level dict mapping records, "
                    f"found {type_name}"
                ]
            )

        record_mapping = cast(dict[object, object], data)
        total_records = len(record_mapping)

        for record_key, record_value in record_mapping.items():
            top_level_key_type_counts[_sde_type_name(record_key)] += 1
            if not isinstance(record_value, dict):
                skipped_record_count += 1
                _append_warning(
                    warnings,
                    (
                        f"Top-level key {record_key!r} has non-dict value "
                        f"{_sde_type_name(record_value)}; skipped"
                    ),
                )
                continue

            valid_record_count += 1
            for field_name, field_value in _mapping_items(record_value):
                node = root_fields.setdefault(str(field_name), _FieldNode())
                node.presence_count += 1
                _update_node_from_value(node, field_value, sde_format)

    else:  # jsonl-model
        if not isinstance(data, list):
            type_name = _sde_type_name(data)
            return _empty_result(
                [f"jsonl-model expects a top-level list of records, found {type_name}"]
            )

        record_list = cast(list[object], data)
        total_records = len(record_list)

        for record_value in record_list:
            if not isinstance(record_value, dict):
                skipped_record_count += 1
                _append_warning(
                    warnings,
                    (
                        f"List item has non-dict value "
                        f"{_sde_type_name(record_value)}; skipped"
                    ),
                )
                continue

            valid_record_count += 1
            for field_name, field_value in _mapping_items(record_value):
                node = root_fields.setdefault(str(field_name), _FieldNode())
                node.presence_count += 1
                _update_node_from_value(node, field_value, sde_format)

    for field_name in sorted(root_fields):
        _collect_node_warnings(field_name, root_fields[field_name], warnings)

    paths = _flatten_field_rows(root_fields, container_count=valid_record_count)

    return {
        "file_name": file_path.name,
        "file_path": str(file_path),
        "sde_format": sde_format,
        "top_level_key_type_counts": _sorted_type_counts(
            dict(top_level_key_type_counts)
        ),
        "total_records": total_records,
        "valid_record_count": valid_record_count,
        "skipped_record_count": skipped_record_count,
        "path_count": len(paths),
        "paths": paths,
        "warnings": warnings,
    }


def _build_schema_report(
    source_path: str,
    datasets: list[DatasetInspection],
    sde_format: SdeFormat,
) -> SchemaReport:
    """Build the top-level schema report object.

    Args:
        source_path: Source file, directory, or glob used for scanning.
        datasets: Dataset inspection results to aggregate.
        sde_format: Source format shared across all scanned datasets.

    Returns:
        Aggregated schema report.
    """
    sorted_datasets = sorted(datasets, key=lambda dataset: dataset["file_name"])
    dataset_map: DatasetMap = {
        dataset["file_name"]: dataset for dataset in sorted_datasets
    }
    all_paths = {path for dataset in sorted_datasets for path in dataset["paths"]}
    total_records = sum(dataset["total_records"] for dataset in sorted_datasets)
    return {
        "source_path": source_path,
        "generated_at_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "sde_format": sde_format,
        "file_count": len(sorted_datasets),
        "total_records": total_records,
        "total_unique_paths": len(all_paths),
        "datasets": dataset_map,
    }


def _collect_files(sde_path: Path, sde_format: SdeFormat) -> list[Path]:
    """Collect dataset files from a path, which may be a file, directory, or glob pattern.

    Args:
        sde_path: Path to a dataset file, or a directory containing dataset files.
        sde_format: Expected top-level structure of the datasets (yaml-model or jsonl-model).

    Returns:
        List of dataset file paths.
    """
    ...


def scan_file(path: Path, sde_format: SdeFormat) -> SchemaReport:
    """Scan a single dataset file and return a schema report.

    Args:
        path: Dataset file to scan (JSON, YAML, or YML).
        sde_format: Expected top-level structure of the dataset.

    Returns:
        Schema report containing one dataset section.
    """
    dataset = _inspect_dataset(path, sde_format)
    return _build_schema_report(str(path), [dataset], sde_format)


def scan_directory(pattern: str | Path, sde_format: SdeFormat) -> SchemaReport:
    """Scan multiple dataset files and return an aggregated schema report.

    Args:
        pattern: Directory, file path, or glob pattern selecting dataset files.
        sde_format: Expected top-level structure of the datasets.

    Returns:
        Schema report with one section per matching dataset file.
    """
    if isinstance(pattern, Path):
        candidate = pattern
        if candidate.is_dir():
            # Collect files with supported extensions (yaml, yml, json).
            yaml_files = set(candidate.glob("*.yaml"))
            yml_files = set(candidate.glob("*.yml"))
            json_files = set(candidate.glob("*.json"))
            files = sorted(yaml_files | yml_files | json_files)
            source_path = str(candidate)
        elif candidate.is_file():
            files = [candidate]
            source_path = str(candidate)
        else:
            files = [Path(match) for match in sorted(glob(str(candidate)))]
            source_path = str(candidate)
    else:
        candidate = Path(pattern)
        if candidate.is_dir():
            # Collect files with supported extensions (yaml, yml, json).
            yaml_files = set(candidate.glob("*.yaml"))
            yml_files = set(candidate.glob("*.yml"))
            json_files = set(candidate.glob("*.json"))
            files = sorted(yaml_files | yml_files | json_files)
        elif candidate.is_file():
            files = [candidate]
        else:
            files = [Path(match) for match in sorted(glob(pattern))]
        source_path = str(pattern)

    datasets = [_inspect_dataset(file_path, sde_format) for file_path in files]
    return _build_schema_report(source_path, datasets, sde_format)


def generate_markdown_report(report: SchemaReport) -> str:
    """Render a human-readable markdown schema report.

    Args:
        report: Schema report from ``scan_file`` or ``scan_directory``.

    Returns:
        Markdown text with a summary and per-dataset sections.
    """
    lines: list[str] = [
        "# Schema Report",
        "",
        "## Summary",
        f"- source_path: {report['source_path']}",
        f"- generated_at_utc: {report['generated_at_utc']}",
        f"- sde_format: {report['sde_format']}",
        f"- files_scanned: {report['file_count']}",
        f"- total_records: {report['total_records']}",
        f"- total_unique_paths: {report['total_unique_paths']}",
        "",
    ]

    for file_name in sorted(report["datasets"]):
        dataset = report["datasets"][file_name]
        key_type_summary = ", ".join(
            f"{type_name}:{count}"
            for type_name, count in dataset["top_level_key_type_counts"].items()
        )
        lines.extend(
            [
                f"## {dataset['file_name']}",
                f"- sde_format: {dataset['sde_format']}",
                f"- Records: {dataset['total_records']}",
                f"- Top-level key types: {key_type_summary or 'unknown'}",
                f"- Valid dict records: {dataset['valid_record_count']}",
                f"- Skipped top-level items: {dataset['skipped_record_count']}",
                f"- Paths discovered: {dataset['path_count']}",
                "",
            ]
        )

        if dataset["paths"]:
            lines.extend(
                [
                    "| Path | Presence | Required | Types |",
                    "|------|----------|----------|-------|",
                ]
            )
            for path in sorted(dataset["paths"]):
                row = dataset["paths"][path]
                type_summary = ", ".join(
                    f"{type_name}:{count}"
                    for type_name, count in row["value_type_counts"].items()
                )
                presence = f"{row['presence_count']}/{row['container_count']}"
                required = "yes" if row["required"] else "no"
                lines.append(f"| {path} | {presence} | {required} | {type_summary} |")
        else:
            lines.append("No schema paths discovered.")

        lines.append("")
        lines.append("### Warnings")
        lines.append("")
        if dataset["warnings"]:
            for warning in dataset["warnings"]:
                lines.append(f"- {warning}")
        else:
            lines.append("- None")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Generate SDE schema report.")
    parser.add_argument(
        "input_path",
        type=str,
        help=(
            "Path to dataset file, directory, or glob pattern to scan. "
            "Examples: 'data.yaml', 'datasets/', 'yaml_files/*.yaml'"
        ),
    )
    parser.add_argument(
        "output_directory",
        type=str,
        help="Path to write the markdown reports.",
    )
    parser.add_argument(
        "--format",
        dest="sde_format",
        choices=["yaml-model", "jsonl-model"],
        default="yaml-model",
        help="Expected top-level structure of the dataset files (default: yaml-model).",
    )
    args = parser.parse_args()

    report = scan_directory(args.input_path, sde_format=args.sde_format)
    markdown = generate_markdown_report(report)

    markdown_report_path = Path(args.output_directory) / "schema_report.md"
    json_report_path = Path(args.output_directory) / "schema_report.json"
    markdown_report_path.parent.mkdir(parents=True, exist_ok=True)
    json_report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(markdown_report_path, "w", encoding="utf-8") as f:
        f.write(markdown)
    with open(json_report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
