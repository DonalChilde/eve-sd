import sqlite3
from pathlib import Path
from typing import Any, cast

from eve_static_data.helpers import json_io
from eve_static_data.helpers.yaml_loader import safe_load_path
from eve_static_data.models.dataset_filenames import SdeDatasets


def load_dataset_from_file(
    dataset: SdeDatasets, *, sde_path: Path
) -> dict[str | int, Any]:
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
    match file_candidates[0].suffix:
        case ".json":
            dataset_dict = json_io.json_load_path(file_candidates[0])
            if not isinstance(dataset_dict, dict):
                raise ValueError(
                    f"Expected a JSON object (dict) in file '{file_candidates[0]}', but got {type(dataset_dict).__name__}."
                )
            cast(dict[str | int, Any], dataset_dict)
            for _, value in dataset_dict.items():
                if "_key" in value:
                    # If "_key" is present, its the jsonl-model format.
                    return dataset_dict
                else:
                    break

            # If "_key" is not present, its the yaml-model format.
            # add the dict ket to record as _record_key
            for record_key, record_value in dataset_dict.items():
                if isinstance(record_value, dict):
                    record_value["_record_key"] = record_key
            return dataset_dict

        case ".yaml" | ".yml":
            ...
        case ".jsonl":
            ...
        case _:
            raise ValueError(
                f"Unsupported file format '{file_candidates[0].suffix}' for dataset '{dataset.value}'."
            )


def load_dataset_from_db(
    dataset: SdeDatasets, *, connection: sqlite3.Connection
) -> dict[str | int, Any]: ...
