"""Load raw SDE datasets from JSONL, JSON, and YAML sources."""

from collections.abc import Iterable
from pathlib import Path
from typing import cast

from eve_static_data import Dataset, KeyedRecord, Record
from eve_static_data.helpers import json_io
from eve_static_data.helpers.yaml_io import safe_load_path


def load_jsonl_as_dataset(jsonl_path: Path) -> Dataset:
    """Load a JSONL file into a dataset mapping.

    Each line in the JSONL file should be a JSON object (dict) with a "_key" field.
    The ``_key`` value is used as the dictionary key in the returned dataset.

    Args:
        jsonl_path: Path to the JSONL file.

    Returns:
        Mapping of record keys to record dictionaries.

    Raises:
        ValueError: If any JSONL line is not a JSON object.
        KeyError: If any JSON object does not include ``_key``.

    Notes:
        When duplicate keys are present, the last record encountered wins.
    """
    dataset_dict: dict[str | int, Record] = {}
    for json_obj in json_io.jsonl_load_path(jsonl_path):
        if not isinstance(json_obj, dict):
            raise ValueError(
                f"Expected each line in JSONL file '{jsonl_path}' to be a JSON object (dict), but got {type(json_obj).__name__}."
            )
        if "_key" not in json_obj:
            raise KeyError(
                f"Expected each JSON object in JSONL file '{jsonl_path}' to contain a '_key' field, but one was missing."
            )
        # The "_key" field can be either a string or an integer, depending on the dataset.
        key = cast(str | int, json_obj["_key"])
        dataset_dict[key] = json_obj
    return dataset_dict


def load_json_as_dataset(json_path: Path) -> Dataset:
    """Load a JSON file into a dataset mapping.

    Args:
        json_path: Path to a JSON file containing a top-level mapping.

    Returns:
        Dataset mapping loaded from the JSON file.

    Raises:
        ValueError: If the JSON top-level value is not an object/mapping.
    """
    dataset_dict = json_io.json_load_path(json_path)
    if not isinstance(dataset_dict, dict):
        raise ValueError(
            f"Expected a JSON object (dict) in file '{json_path}', but got {type(dataset_dict).__name__}."
        )
    dataset_dict = cast(dict[str | int, Record], dataset_dict)
    return dataset_dict


def load_yaml_as_dataset(yaml_path: Path) -> Dataset:
    """Load a YAML file into a dataset mapping.

    Args:
        yaml_path: Path to a YAML file containing a top-level mapping.

    Returns:
        Dataset mapping loaded from the YAML file.

    Raises:
        ValueError: If the YAML top-level value is not a mapping.
    """
    dataset_dict = safe_load_path(yaml_path)
    if not isinstance(dataset_dict, dict):
        raise ValueError(
            f"Expected a YAML mapping (dict) in file '{yaml_path}', but got {type(dataset_dict).__name__}."
        )
    dataset_dict = cast(Dataset, dataset_dict)
    return dataset_dict


def load_jsonl_as_records(
    jsonl_path: Path,
) -> Iterable[KeyedRecord]:
    """Yield keyed records from a JSONL file.

    Each line in the JSONL file should be a JSON object (dict) with a "_key" field.
    The ``_key`` value is emitted as the first element of each yielded tuple.

    Args:
        jsonl_path: Path to the JSONL file.

    Yields:
        ``(record_key, record)`` tuples for each JSONL line.

    Raises:
        ValueError: If any JSONL line is not a JSON object.
        KeyError: If any JSON object does not include ``_key``.
    """
    for json_obj in json_io.jsonl_load_path(jsonl_path):
        if not isinstance(json_obj, dict):
            raise ValueError(
                f"Expected each line in JSONL file '{jsonl_path}' to be a JSON object (dict), but got {type(json_obj).__name__}."
            )
        if "_key" not in json_obj:
            raise KeyError(
                f"Expected each JSON object in JSONL file '{jsonl_path}' to contain a '_key' field, but one was missing."
            )
        # The "_key" field can be either a string or an integer, depending on the dataset.
        json_obj = cast(Record, json_obj)
        key = json_obj["_key"]
        yield (key, json_obj)
