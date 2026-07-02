"""Load and validate SDE metadata from files, archives, or databases."""

import sqlite3
import zipfile
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

from pydantic import RootModel

from eve_static_data.helpers import json_io, yaml_io
from eve_static_data.helpers.load_raw_datasets import (
    load_jsonl_as_dataset,
    load_yaml_as_dataset,
)


class SdeVariant(StrEnum):
    """Logical source format of an SDE dataset."""

    YAML = "yaml"
    JSONL = "jsonl"


class SourceMedia(StrEnum):
    """File/media extension used by the current SDE source."""

    YAML = ".yaml"
    JSONL = ".jsonl"
    JSON = ".json"
    DB = ".db"


@dataclass(slots=True, kw_only=True)
class SdeMetadata:
    """Normalized SDE metadata model.

    This dataclass represents metadata loaded from ``_sde.jsonl`` or
    ``_sde.yaml``, with additional information.
    """

    buildNumber: int
    releaseDate: str
    variant: SdeVariant
    source_media: SourceMedia


SdeMetadataRoot = RootModel[SdeMetadata]


def load_sde_metadata(input_path: Path) -> SdeMetadata:
    """Load SDE metadata from a dataset directory.

    The directory must contain exactly one metadata file:
    ``_sde.jsonl`` or ``_sde.yaml``.

    Args:
        input_path: Path to a directory containing SDE dataset files.

    Returns:
        Parsed and normalized metadata.

    Raises:
        FileNotFoundError: If neither metadata file exists.
        ValueError: If both metadata files exist.
        KeyError: If expected metadata keys are missing.
    """
    sde_info_path_yaml = input_path / "_sde.yaml"
    sde_info_path_jsonl = input_path / "_sde.jsonl"

    existing_metadata_files: list[Path] = [
        path for path in (sde_info_path_yaml, sde_info_path_jsonl) if path.exists()
    ]

    if not existing_metadata_files:
        raise FileNotFoundError(
            f"No _sde.jsonl or _sde.yaml file found at {input_path}."
        )
    if len(existing_metadata_files) > 1:
        found_names = ", ".join(path.name for path in existing_metadata_files)
        raise ValueError(
            f"Multiple _sde metadata files found at {input_path}: {found_names}. "
            "Expected exactly one metadata file."
        )

    if sde_info_path_jsonl.exists():
        sde_dataset = load_jsonl_as_dataset(sde_info_path_jsonl)

        values: dict[str, Any] = {
            "buildNumber": sde_dataset["sde"]["buildNumber"],
            "releaseDate": sde_dataset["sde"]["releaseDate"],
            "variant": SdeVariant.JSONL,
            "source_media": SourceMedia.JSONL,
        }
        return SdeMetadataRoot.model_validate(values).root
    elif sde_info_path_yaml.exists():
        sde_dataset = load_yaml_as_dataset(sde_info_path_yaml)
        values: dict[str, Any] = {
            "buildNumber": sde_dataset["sde"]["buildNumber"],
            "releaseDate": sde_dataset["sde"]["releaseDate"],
            "variant": SdeVariant.YAML,
            "source_media": SourceMedia.YAML,
        }
        return SdeMetadataRoot.model_validate(values).root
    else:
        raise FileNotFoundError(
            f"No _sde.jsonl or _sde.yaml file found at {input_path}."
        )


def load_sde_metadata_from_zipfile(sde_zip_file: Path) -> SdeMetadata:
    """Load SDE metadata from a downloaded SDE zip archive.

    Args:
        sde_zip_file: Path to an SDE zip archive.

    Returns:
        Parsed and normalized metadata from the archive.

    Raises:
        FileNotFoundError: If neither metadata file exists in the archive.
        ValueError: If both metadata files exist in the archive.
        KeyError: If expected metadata keys are missing.
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
                sde_info = json_io.json_loads(first_line)
                values: dict[str, Any] = {
                    "buildNumber": sde_info["buildNumber"],
                    "releaseDate": sde_info["releaseDate"],
                    "variant": SdeVariant.JSONL,
                    "source_media": SourceMedia.JSONL,
                }
                return SdeMetadataRoot.model_validate(values).root
        else:
            with zip_ref.open("_sde.yaml") as f:
                sde_info = yaml_io.safe_load_IO(f)
                sde_info = sde_info["sde"]
                values: dict[str, Any] = {
                    "buildNumber": sde_info["buildNumber"],
                    "releaseDate": sde_info["releaseDate"],
                    "variant": SdeVariant.YAML,
                    "source_media": SourceMedia.YAML,
                }
            return SdeMetadataRoot.model_validate(values).root


def load_sde_metadata_from_db(connection: sqlite3.Connection) -> SdeMetadata:
    """Load SDE metadata from an SQLite connection.

    This function is currently a placeholder and has not been implemented.

    Args:
        connection: Open SQLite connection.

    Returns:
        SDE metadata loaded from database tables.
    """
    ...
