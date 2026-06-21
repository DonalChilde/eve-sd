"""Helper functions for loading raw datasets from files or databases."""

import sqlite3
from pathlib import Path
from typing import Any, cast

from eve_static_data.helpers import json_io
from eve_static_data.helpers.yaml_loader import safe_load_path
from eve_static_data.models.dataset_filenames import SdeDatasets


def _load_jsonl_as_dict(jsonl_path: Path) -> dict[str | int, Any]:
    dataset_dict: dict[str | int, Any] = {}
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


def _load_json_as_dict(json_path: Path) -> dict[str | int, Any]:
    dataset_dict = json_io.json_load_path(json_path)
    if not isinstance(dataset_dict, dict):
        raise ValueError(
            f"Expected a JSON object (dict) in file '{json_path}', but got {type(dataset_dict).__name__}."
        )
    dataset_dict = cast(dict[str | int, Any], dataset_dict)
    return dataset_dict


def _load_yaml_as_dict(yaml_path: Path) -> dict[str | int, Any]:
    dataset_dict = safe_load_path(yaml_path)
    if not isinstance(dataset_dict, dict):
        raise ValueError(
            f"Expected a YAML mapping (dict) in file '{yaml_path}', but got {type(dataset_dict).__name__}."
        )
    dataset_dict = cast(dict[str | int, Any], dataset_dict)
    return dataset_dict


def load_dataset_from_file(
    dataset: SdeDatasets, *, sde_path: Path
) -> dict[str | int, Any]:
    """Loads a dataset from a file in the given SDE path.

    Automatically detects the file format (JSONL, YAML, or JSON) and
    source model (jsonl-model or yaml-model).
    """
    if not sde_path.exists() or not sde_path.is_dir():
        raise NotADirectoryError(f"Provided SDE path '{sde_path}' is not a directory.")
    file_candidates = list(sde_path.glob(f"{dataset.value}.*"))
    if not file_candidates:
        raise FileNotFoundError(
            f"No file found for dataset '{dataset.value}' in '{sde_path}'."
        )
    if len(file_candidates) > 1:
        raise FileExistsError(
            f"Multiple files found for dataset '{dataset.value}' in '{sde_path}': {file_candidates}"
        )
    source_format = ""
    match file_candidates[0].suffix:
        case ".json":
            dataset_dict = _load_json_as_dict(file_candidates[0])
            for _, value in dataset_dict.items():
                if "_key" in value:
                    # If "_key" is present, its the jsonl-model format.
                    source_format = "jsonl-model"
                    break
                else:
                    # If "_key" is not present, its the yaml-model format.
                    source_format = "yaml-model"
                    break

        case ".yaml" | ".yml":
            dataset_dict = _load_yaml_as_dict(file_candidates[0])
            source_format = "yaml-model"
        case ".jsonl":
            source_format = "jsonl-model"
            dataset_dict = _load_jsonl_as_dict(file_candidates[0])
        case _:
            raise ValueError(
                f"Unsupported file format '{file_candidates[0].suffix}' for dataset '{dataset.value}'."
            )
    if source_format == "jsonl-model":
        # No further processing needed.
        return dataset_dict
    elif source_format == "yaml-model":
        # Add the "_record_key" field to each record in the dataset, using the key from the YAML mapping.
        for key, value in dataset_dict.items():
            value["_record_key"] = key
        return dataset_dict
    else:
        raise ValueError(
            f"Could not determine source format for dataset '{dataset.value}' from file '{file_candidates[0]}'."
        )


def load_dataset_from_db(
    dataset: SdeDatasets, *, connection: sqlite3.Connection
) -> dict[str | int, Any]: ...
