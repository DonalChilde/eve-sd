"""Generate schema inspection reports for normalized SDE datasets.

This module is the data-first canonical implementation for schema reporting.
It accepts already-normalized dataset mappings and does not perform any file I/O.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Literal, TypedDict, cast

from eve_sd.helpers.sde_metadata import SdeMetadata

SdeTypeName = Literal["dict", "list", "str", "int", "float", "bool", "null"]
SdeFormat = Literal["yaml-model", "jsonl-model"]

type PathStatsMap = dict[str, "PathInspection"]
type DatasetMap = dict[str, "DatasetInspection"]
type WarningList = list[str]

#: Sentinel path component used in top-level key summaries for integer keys.
INTEGER_KEY = "INTEGER_KEY"

#: Sentinel path component used in top-level key summaries for string keys.
STRING_KEY = "STRING_KEY"


def _string_counter() -> Counter[str]:
    return Counter()


def _field_node_map() -> dict[str, _FieldNode]:
    return {}


class DatasetInput(TypedDict):
    """Input tuple for one normalized dataset."""

    dataset_name: str
    dataset_data: dict[int | str, Any]
    sde_metadata: SdeMetadata


class PathInspection(TypedDict):
    """Flattened inspection data for one dotted field path."""

    path: str
    presence_count: int
    container_count: int
    required: bool
    value_type_counts: dict[str, int]


class DatasetInspection(TypedDict):
    """Inspection output for one normalized dataset."""

    dataset_name: str
    dataset_source: str
    sde_metadata: SdeMetadata
    top_level_key_type_counts: dict[str, int]
    total_records: int
    valid_record_count: int
    skipped_record_count: int
    path_count: int
    paths: PathStatsMap
    warnings: WarningList


class SchemaReport(TypedDict):
    """Top-level schema report for one or more datasets."""

    source_path: str
    generated_at_utc: str
    sde_metadata: SdeMetadata
    file_count: int
    total_records: int
    total_unique_paths: int
    datasets: DatasetMap


@dataclass
class _ListStats:
    item_count: int = 0
    item_type_counts: Counter[str] = field(default_factory=_string_counter)
    empty_list_count: int = 0
    item_node: _FieldNode = field(default_factory=lambda: _FieldNode())


@dataclass
class _FieldNode:
    presence_count: int = 0
    value_type_counts: Counter[str] = field(default_factory=_string_counter)
    children: dict[str, _FieldNode] = field(default_factory=_field_node_map)
    list_stats: _ListStats | None = None


def _sde_type_name(value: Any) -> SdeTypeName:
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
    return list(cast(dict[object, object], value).items())


def _sequence_items(value: Any) -> list[object]:
    return list(cast(list[object], value))


def _top_level_key_bucket(key: object) -> str:
    return INTEGER_KEY if isinstance(key, int) else STRING_KEY


def _sorted_type_counts(type_counts: dict[str, int]) -> dict[str, int]:
    keys = sorted(type_counts)
    return {key: type_counts[key] for key in keys}


def _append_warning(warnings: WarningList, message: str) -> None:
    if message not in warnings:
        warnings.append(message)


def _update_node_from_value(node: _FieldNode, value: Any) -> None:
    type_name = _sde_type_name(value)
    node.value_type_counts[type_name] += 1

    if isinstance(value, dict):
        for child_name, child_value in _mapping_items(value):
            child_key = str(child_name)
            child_node = node.children.setdefault(child_key, _FieldNode())
            child_node.presence_count += 1
            _update_node_from_value(child_node, child_value)
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
            _update_node_from_value(list_stats.item_node, item)


def _flatten_field_rows(
    fields: dict[str, _FieldNode],
    container_count: int,
    prefix: str = "",
    ancestor_required: bool = True,
) -> PathStatsMap:
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


def _collect_node_warnings(path: str, node: _FieldNode, warnings: WarningList) -> None:
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


def _inspect_dataset_data(
    dataset_name: str,
    dataset_data: dict[int | str, Any],
    sde_metadata: SdeMetadata,
    *,
    dataset_source: str | None = None,
) -> DatasetInspection:
    warnings: WarningList = []
    root_fields: dict[str, _FieldNode] = {}
    top_level_key_type_counts: Counter[str] = _string_counter()
    dataset_source = dataset_source or dataset_name

    total_records = len(dataset_data)
    valid_record_count = 0
    skipped_record_count = 0

    for record_key, record_value in dataset_data.items():
        top_level_key_type_counts[_top_level_key_bucket(record_key)] += 1
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
            _update_node_from_value(node, field_value)

    for field_name in sorted(root_fields):
        _collect_node_warnings(field_name, root_fields[field_name], warnings)

    paths = _flatten_field_rows(root_fields, container_count=valid_record_count)

    return {
        "dataset_name": dataset_name,
        "dataset_source": dataset_source,
        "sde_metadata": sde_metadata,
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


def inspect_dataset_data(
    dataset_name: str,
    dataset_data: dict[int | str, Any],
    sde_metadata: SdeMetadata,
    *,
    dataset_source: str | None = None,
) -> DatasetInspection:
    """Inspect one normalized dataset mapping.

    Args:
        dataset_name: Logical dataset name used as the report key.
        dataset_data: Normalized top-level mapping of record keys to records.
        sde_metadata: SDE metadata for the dataset.
        dataset_source: Optional source label for display in the report.

    Returns:
        Dataset inspection data for the supplied mapping.
    """
    return _inspect_dataset_data(
        dataset_name=dataset_name,
        dataset_data=dataset_data,
        sde_metadata=sde_metadata,
        dataset_source=dataset_source,
    )


def _build_schema_report(
    source_path: str,
    datasets: list[DatasetInspection],
    sde_metadata: SdeMetadata,
) -> SchemaReport:
    sorted_datasets = sorted(datasets, key=lambda dataset: dataset["dataset_name"])
    dataset_map: DatasetMap = {
        dataset["dataset_name"]: dataset for dataset in sorted_datasets
    }
    all_paths = {path for dataset in sorted_datasets for path in dataset["paths"]}
    total_records = sum(dataset["total_records"] for dataset in sorted_datasets)
    return {
        "source_path": source_path,
        "generated_at_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "sde_metadata": sde_metadata,
        "file_count": len(sorted_datasets),
        "total_records": total_records,
        "total_unique_paths": len(all_paths),
        "datasets": dataset_map,
    }


def build_schema_report(
    datasets: Iterable[DatasetInput],
    sde_metadata: SdeMetadata,
    *,
    dataset_source: str,
) -> SchemaReport:
    """Build a schema report from multiple normalized datasets.

    Args:
        datasets: Iterable of DatasetInput dicts containing dataset name, data mapping, and metadata.
        sde_metadata: SDE metadata to include in the report summary.
        dataset_source: Display label for the aggregate source in the report.

    Returns:
        Combined schema report covering all datasets.
    """
    inspected_datasets: list[DatasetInspection] = []

    for inspection_args in datasets:
        inspected_datasets.append(
            _inspect_dataset_data(**inspection_args, dataset_source=dataset_source)
        )

    return _build_schema_report(dataset_source, inspected_datasets, sde_metadata)
