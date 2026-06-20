"""Functions for loading a YAML based SDE to the sqlite database."""

import logging
import sqlite3
from pathlib import Path
from typing import Any, Literal, cast

from more_itertools import peekable
from pydantic_core import from_json

from eve_static_data.db.primary.helpers import (
    write_int_records,
    write_key_type,
    write_sde_metadata,
    write_str_records,
)
from eve_static_data.db.primary.models import DatasetRecordInt, DatasetRecordStr
from eve_static_data.helpers.sde_metadata import load_sde_metadata
from eve_static_data.helpers.yaml_loader import safe_load_path

logger = logging.getLogger(__name__)


def import_yaml_sde_to_db(sde_path: Path, *, connection: sqlite3.Connection) -> None:
    """Load the SDE datasets from the given input path to the sqlite database using the provided connection.

    This function reads the SDE datasets from the given input path, which should contain
    YAML files for each dataset. It then parses the YAML files and inserts the records
    into the sqlite database at db_path. The function also reads the SDE metadata from
    a `_sde.yaml` file in the input path and inserts it into the database.

    Uses the CSafeLoader for YAML parsing if available, otherwise falls back to the SafeLoader.

    Args:
        sde_path: The path to the directory containing the SDE datasets in YAML format.
        connection: The sqlite database connection where the SDE data should be inserted.
    """
    # Load the SDE metadata from the _sde.yaml file
    sde_metadata = load_sde_metadata(sde_path)
    if sde_metadata.source_format != "yaml-model":
        raise ValueError(
            f"Expected source format 'yaml-model' in SDE metadata, but got '{sde_metadata.source_format}'."
        )
    # And insert the SDE metadata into the database
    write_sde_metadata(connection, sde_metadata)

    # Iterate over the YAML files in the input path and insert the records into the database
    # YAML format datasets are dicts of records, where the key is either an int or
    # a str, and the value is the record dict
    yaml_files = list(sde_path.glob("*.yaml"))
    if not yaml_files:
        raise ValueError(f"No YAML files found in {sde_path}.")
    logger.info(
        f"Found {len(yaml_files)} YAML files in {sde_path} to load into the database."
    )
    for yaml_file in yaml_files:
        logger.info(f"Loading dataset from {yaml_file} into the database.")
        dataset_name = yaml_file.stem

        dataset_records = safe_load_path(yaml_file)

        if not isinstance(dataset_records, dict):
            raise ValueError(
                f"Expected a dict of records in {yaml_file}, but got {type(dataset_records)}"
            )

        if not dataset_records:
            raise ValueError(f"No records found in {yaml_file}.")
        dataset_records = cast(dict[str | int, Any], dataset_records)
        # Get key type and write it to the database.
        key_type = _write_yaml_key_type(
            dataset_records, dataset_name, connection=connection
        )
        match key_type:
            case "int":
                dataset_records = cast(dict[int, Any], dataset_records)
                records = (
                    DatasetRecordInt.from_yaml_record(dataset_name, key, value)
                    for key, value in dataset_records.items()
                )
                write_int_records(records, connection=connection)
            case "str":
                dataset_records = cast(dict[str, Any], dataset_records)
                records = (
                    DatasetRecordStr.from_yaml_record(dataset_name, key, value)
                    for key, value in dataset_records.items()
                )
                write_str_records(records, connection=connection)
            case _:
                raise ValueError(
                    f"Unexpected key type {key_type} for dataset {dataset_name} in {yaml_file}."
                )


def import_jsonl_sde_to_db(sde_path: Path, *, connection: sqlite3.Connection) -> None:
    """Load the SDE datasets from the given input path to the sqlite database using the provided connection.

    This function reads the SDE datasets from the given input path, which should contain
    JSONL files for each dataset. It then parses the JSONL files and inserts the records
    into the sqlite database at db_path. The function also reads the SDE metadata from
    a `_sde.jsonl` file in the input path and inserts it into the database.

    Args:
        sde_path: The path to the directory containing the SDE datasets in JSONL format.
        connection: The sqlite database connection where the SDE data should be inserted.
    """
    # Load the SDE metadata from the _sde.jsonl file
    sde_metadata = load_sde_metadata(sde_path)
    if sde_metadata.source_format != "jsonl-model":
        raise ValueError(
            f"Expected source format 'jsonl-model' in SDE metadata, but got '{sde_metadata.source_format}'."
        )
    # And insert the SDE metadata into the database
    write_sde_metadata(connection, sde_metadata)

    # Iterate over the JSONL files in the input path and insert the records into the database
    # JSONL format datasets are lists of records, where each record is a dict with a
    # top-level key '_key' that contains either an int or a str, and other keys for the
    # record data
    jsonl_files = list(sde_path.glob("*.jsonl"))
    if not jsonl_files:
        raise ValueError(f"No JSONL files found in {sde_path}.")
    logger.info(
        f"Found {len(jsonl_files)} JSONL files in {sde_path} to load into the database."
    )
    for jsonl_file in jsonl_files:
        logger.info(f"Loading dataset from {jsonl_file} into the database.")
        dataset_name = jsonl_file.stem
        with jsonl_file.open() as f:
            dataset_record_objects = (from_json(line) for line in f)
            peekable_records = peekable(dataset_record_objects)
            first_record = peekable_records.peek(None)
            if first_record is None:
                raise ValueError(f"No records found in {jsonl_file}.")
            key_type = _write_jsonl_key_type(
                first_record, dataset_name, connection=connection
            )
            match key_type:
                case "int":
                    records = (
                        DatasetRecordInt.from_jsonl_record(dataset_name, record)
                        for record in peekable_records
                    )
                    write_int_records(records, connection=connection)
                case "str":
                    records = (
                        DatasetRecordStr.from_jsonl_record(dataset_name, record)
                        for record in peekable_records
                    )
                    write_str_records(records, connection=connection)
                case _:
                    raise ValueError(
                        f"Unexpected key type {key_type} for dataset {dataset_name} in {jsonl_file}."
                    )


def _write_jsonl_key_type(
    jsonl_record: dict[str, Any], dataset_name: str, *, connection: sqlite3.Connection
) -> Literal["int", "str"]:
    """Helper function to write the key type of a dataset to the database."""
    key_type = "unknown"
    record_key = jsonl_record.get("_key")
    if isinstance(record_key, int):
        key_type = "int"
    elif isinstance(record_key, str):  # pyright: ignore[reportUnnecessaryIsInstance]
        key_type = "str"
    else:
        raise ValueError(
            f"Expected record key in dataset {dataset_name} to be either int or str, but got {type(record_key)} for key {record_key}"
        )
    if key_type == "unknown":  # pyright: ignore[reportUnnecessaryComparison]
        raise ValueError(
            f"Could not determine key type for records in dataset {dataset_name}."
        )
    write_key_type(connection, dataset_name, key_type)
    return key_type


def _write_yaml_key_type(
    yaml_records: dict[str | int, Any],
    dataset_name: str,
    *,
    connection: sqlite3.Connection,
) -> Literal["int", "str"]:
    """Helper function to write the key type of a dataset to the database."""
    key_type = "unknown"
    # Check the key type of the first record to determine the key type for
    # the entire dataset. We assume that all keys in the dataset have the
    # same type, so we only check the first one.
    for key in yaml_records.keys():
        if isinstance(key, int):
            key_type = "int"
            break
        elif isinstance(key, str):  # pyright: ignore[reportUnnecessaryIsInstance]
            key_type = "str"
            break
        else:
            raise ValueError(
                f"Expected record keys in dataset {dataset_name} to be either int or str, but got {type(key)} for key {key}"
            )
    if key_type == "unknown":
        raise ValueError(
            f"Could not determine key type for records in dataset {dataset_name}."
        )
    write_key_type(connection, dataset_name, key_type)
    return key_type
