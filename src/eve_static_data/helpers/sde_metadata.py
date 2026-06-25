"""Functions for loading SDE info from a given input path or SDE zip file."""

import json
import sqlite3
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from pydantic import RootModel

from eve_static_data.helpers.yaml_io import safe_load_IO, safe_load_path


@dataclass(slots=True, kw_only=True)
class SdeMetadata:
    """TypedDict for the SDE info.

    Can represent the info from either the _sde.jsonl or _sde.yaml file, as they have
    the same data, with slightly different structure.
    """

    buildNumber: int
    releaseDate: str
    source_format: Literal["yaml-model", "jsonl-model"] | None = None


SdeMetadataRoot = RootModel[SdeMetadata]


def load_sde_metadata(input_path: Path) -> SdeMetadata:
    """Get the SDE metadata from the given input path.

    The input_path usually points to a directory containing the SDE datasets for a specific
    build number, and should include a `_sde.jsonl` or `_sde.yaml` file with the SDE info. This function
    reads the first line of the `_sde.jsonl` or the `_sde.yaml` file, which should contain the SDE info in
    JSON format, and returns it as an SdeInfo TypedDict.

    Example of the expected output from the `_sde.jsonl` file:
    ```json
    {
        "_key": "sde",
        "buildNumber": 123456,
        "releaseDate": "2024-01-01"
    }
    ```

    Example of the expected output from the `_sde.yaml` file:

    ```yaml
    sde:
      buildNumber: 3393779
      releaseDate: '2026-06-14T11:47:47Z'
    ```

    Args:
        input_path: The path to the directory containing the SDE datasets and the `_sde.jsonl` or `_sde.yaml` file.

    Returns:
        An SdeMetadata containing the SDE info from the `_sde.jsonl` or `_sde.yaml` file.

    Raises:
        FileNotFoundError: If the `_sde.jsonl` or `_sde.yaml` file is not found at the given input path.
        json.JSONDecodeError: If the first line of the `_sde.jsonl` file is not valid JSON.
        KeyError: If the expected keys are not found in the JSON data.
    """
    sde_info_path_yaml = input_path / "_sde.yaml"
    sde_info_path_jsonl = input_path / "_sde.jsonl"
    sde_info_path_json = input_path / "_sde.json"

    if not sde_info_path_jsonl.exists() and not sde_info_path_yaml.exists():
        raise FileNotFoundError(
            f"_sde.jsonl or _sde.yaml file not found at {input_path}."
        )
    if sde_info_path_jsonl.exists() and sde_info_path_yaml.exists():
        raise ValueError(
            f"Both _sde.jsonl and _sde.yaml files found at {input_path}. Expected only one of them."
        )
    if sde_info_path_jsonl.exists():
        with open(sde_info_path_jsonl) as f:
            first_line = f.readline()
            sde_info = json.loads(first_line)
            values: dict[str, Any] = {
                "buildNumber": sde_info["buildNumber"],
                "releaseDate": sde_info["releaseDate"],
                "source_format": "jsonl-model",
            }
            return SdeMetadataRoot.model_validate(values).root
    elif sde_info_path_yaml.exists():
        sde_info = safe_load_path(sde_info_path_yaml)
        values: dict[str, Any] = {
            "buildNumber": sde_info["sde"]["buildNumber"],
            "releaseDate": sde_info["sde"]["releaseDate"],
            "source_format": "yaml-model",
        }
        return SdeMetadataRoot.model_validate(values).root
    elif sde_info_path_json.exists():
        with open(sde_info_path_json) as f:
            sde_info = json.load(f)
            # If "_key" is present, its the jsonl-model format.
            has_key = "_key" in sde_info
            if has_key:
                values: dict[str, Any] = {
                    "buildNumber": sde_info["buildNumber"],
                    "releaseDate": sde_info["releaseDate"],
                    "source_format": "jsonl-model",
                }
            else:
                values: dict[str, Any] = {
                    "buildNumber": sde_info["sde"]["buildNumber"],
                    "releaseDate": sde_info["sde"]["releaseDate"],
                    "source_format": "yaml-model",
                }
            return SdeMetadataRoot.model_validate(values).root
    else:
        raise FileNotFoundError(
            f"No _sde.jsonl, _sde.yaml, or _sde.json file found at {input_path}."
        )


def load_sde_metadata_from_zipfile(sde_zip_file: Path) -> SdeMetadata:
    """Get the SDE metadata from the given SDE zip file.

    This function opens the given SDE zip file, looks for the `_sde.jsonl` or `_sde.yaml` file inside it,
    reads the first line of that file (for JSONL) or loads the YAML content, and
    returns it as an SdeMetadata instance.

    Args:
        sde_zip_file: The path to the SDE zip file.

    Returns:
        An SdeMetadata containing the SDE info from the `_sde.jsonl` or `_sde.yaml` file inside the zip file.

    Raises:
        FileNotFoundError: If neither the `_sde.jsonl` nor `_sde.yaml` file is found inside the zip file.
        json.JSONDecodeError: If the first line of the `_sde.jsonl` file is not valid JSON.
        KeyError: If the expected keys are not found in the JSON or YAML data.
    """
    with zipfile.ZipFile(sde_zip_file, "r") as zip_ref:
        info_yaml = zipfile.Path(zip_ref) / "_sde.yaml"
        info_jsonl = zipfile.Path(zip_ref) / "_sde.jsonl"
        if not info_yaml.exists() and not info_jsonl.exists():
            raise FileNotFoundError(
                f"_sde.jsonl or _sde.yaml file not found in the zip file {sde_zip_file}."
            )
        if info_yaml.exists() and info_jsonl.exists():
            raise ValueError(
                f"Both _sde.jsonl and _sde.yaml files found in the zip file {sde_zip_file}. Expected only one of them."
            )
        if info_jsonl.exists():
            with zip_ref.open("_sde.jsonl") as f:
                first_line = f.readline().decode("utf-8")
                sde_info = json.loads(first_line)
                values: dict[str, Any] = {
                    "buildNumber": sde_info["buildNumber"],
                    "releaseDate": sde_info["releaseDate"],
                    "source_format": "jsonl",
                }
                return SdeMetadataRoot.model_validate(values).root
        else:
            with zip_ref.open("_sde.yaml") as f:
                sde_info = safe_load_IO(f)
                sde_info = sde_info["sde"]
                values: dict[str, Any] = {
                    "buildNumber": sde_info["buildNumber"],
                    "releaseDate": sde_info["releaseDate"],
                    "source_format": "yaml",
                }
            return SdeMetadataRoot.model_validate(values).root


def load_sde_metadata_from_sqlite(connection: sqlite3.Connection) -> SdeMetadata:
    """Get the SDE metadata from the given SDE SQLite database connection.

    This function opens the given SDE SQLite database file, queries the `sde_info` table
    for the build number and release date, and returns it as an SdeMetadata instance.

    Args:
        connection: The SQLite database connection.

    Returns:
        An SdeMetadata containing the SDE info from the `sde_info` table.

    Raises:
        sqlite3.DatabaseError: If there is an error querying the database.
    """
    raise NotImplementedError(
        "Loading SDE metadata from SQLite is not yet implemented."
    )
    ...
