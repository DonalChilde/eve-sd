"""Helper functions for loading raw datasets from files."""

from collections.abc import Iterable
from pathlib import Path
from typing import cast

from eve_static_data import Dataset, KeyedRecord, Record
from eve_static_data.helpers import json_io
from eve_static_data.helpers.yaml_io import safe_load_path


def load_jsonl_as_dataset(jsonl_path: Path) -> Dataset:
    """Loads a JSONL file as a dataset dictionary.

    Each line in the JSONL file should be a JSON object (dict) with a "_key" field.
    The "_key" field will be used as the key in the returned dataset dictionary.

    Args:
        jsonl_path: Path to the JSONL file.

    Returns:
        Dataset: A dictionary mapping record keys to record dictionaries.
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
    """Loads a JSON file as a dataset dictionary."""
    dataset_dict = json_io.json_load_path(json_path)
    if not isinstance(dataset_dict, dict):
        raise ValueError(
            f"Expected a JSON object (dict) in file '{json_path}', but got {type(dataset_dict).__name__}."
        )
    dataset_dict = cast(dict[str | int, Record], dataset_dict)
    return dataset_dict


def load_yaml_as_dataset(yaml_path: Path) -> Dataset:
    """Loads a YAML file as a dataset dictionary."""
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
    """Load a JSONL file as an iterable of records.

    Each line in the JSONL file should be a JSON object (dict) with a "_key" field.
    The "_key" field will be used as the key in the returned iterable of records.

    Args:
        jsonl_path: Path to the JSONL file.

    Returns:
        Iterable[KeyedRecord]: An iterable of tuples, each containing a record key and the corresponding record dictionary.
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
