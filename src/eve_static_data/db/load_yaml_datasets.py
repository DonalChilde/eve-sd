"""Load the SDE datasets from YAML files into a sqlite database."""

import logging
import sqlite3
from pathlib import Path
from typing import Any, Literal, cast

from eve_static_data.db import models_2 as db_models
from eve_static_data.db.helpers import (
    write_int_records,
    write_key_type,
    write_sde_metadata,
    write_str_records,
)
from eve_static_data.helpers.sde_metadata import load_sde_metadata
from eve_static_data.helpers.yaml_io import safe_load_path

logger = logging.getLogger(__name__)


def import_yaml_sde_to_db(
    sde_path: Path,
    *,
    connection: sqlite3.Connection,
    serialization_format: db_models.SerializationFormat = db_models.SerializationFormat.PICKLE,
) -> None:
    """Load YAML SDE datasets into sqlite and serialize each record as bytes.

    This loader reads the dataset YAML files and the `_sde.yaml` metadata file from
    ``sde_path``, then stores the parsed records in the provided sqlite connection.
    The chosen ``serialization_format`` only affects how each record payload is stored
    in the database after parsing.

    Format tradeoffs:
    - ``YAML`` keeps the stored payload human-readable and can preserve the original
        mapping shape more naturally, but it is slower to serialize and deserialize.
    - ``JSON`` is widely interoperable and compact, but YAML datasets with integer
        mapping keys will be normalized to strings when they are serialized as JSON.
    - ``PICKLE`` is usually the fastest option and round-trips Python objects most
        faithfully, but it is Python-specific, not human-readable, and should only be
        used with trusted data.

    The loader expects the input directory to contain YAML files for each dataset and
    a ``_sde.yaml`` metadata file. YAML parsing uses ``CSafeLoader`` when available,
    otherwise it falls back to ``SafeLoader``.

    Args:
            sde_path: Directory containing the YAML datasets to import.
            connection: Open sqlite connection that receives the imported rows.
            serialization_format: Byte format used to store each record in the database.
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
        key_type = _yaml_key_type(dataset_records, dataset_name)
        write_key_type(
            connection,
            dataset_name=dataset_name,
            key_type=key_type,
            serialization_format=serialization_format,
        )
        match key_type:
            case "int":
                dataset_records = cast(dict[int, Any], dataset_records)
                match serialization_format:
                    case db_models.SerializationFormat.YAML:
                        record_class = db_models.DatasetRecordIntYaml
                    case db_models.SerializationFormat.JSON:
                        record_class = db_models.DatasetRecordIntJson
                    case db_models.SerializationFormat.PICKLE:
                        record_class = db_models.DatasetRecordIntPickle
                    case _:
                        raise ValueError(
                            f"Unexpected serialization format {serialization_format} for dataset {dataset_name} in {yaml_file}."
                        )
                records = (
                    record_class.from_record(dataset_name, key, value)
                    for key, value in dataset_records.items()
                )
                write_int_records(connection, records=records)
            case "str":
                dataset_records = cast(dict[str, Any], dataset_records)
                match serialization_format:
                    case db_models.SerializationFormat.YAML:
                        record_class = db_models.DatasetRecordStrYaml
                    case db_models.SerializationFormat.JSON:
                        record_class = db_models.DatasetRecordStrJson
                    case db_models.SerializationFormat.PICKLE:
                        record_class = db_models.DatasetRecordStrPickle
                    case _:
                        raise ValueError(
                            f"Unexpected serialization format {serialization_format} for dataset {dataset_name} in {yaml_file}."
                        )
                records = (
                    record_class.from_record(dataset_name, key, value)
                    for key, value in dataset_records.items()
                )
                write_str_records(connection, records=records)
            case _:
                raise ValueError(
                    f"Unexpected key type {key_type} for dataset {dataset_name} in {yaml_file}."
                )


def _yaml_key_type(
    yaml_records: dict[str | int, Any], dataset_name: str
) -> Literal["int", "str"]:
    """Helper function to determine the key type of a dataset."""
    # Check the key type of the first record to determine the key type for
    # the entire dataset. We assume that all keys in the dataset have the
    # same type, so we only check the first one.
    for key in yaml_records.keys():
        if isinstance(key, int):
            key_type = "int"
            return key_type
        elif isinstance(key, str):  # pyright: ignore[reportUnnecessaryIsInstance]
            key_type = "str"
            return key_type
        else:
            raise ValueError(
                f"Expected record keys in dataset {dataset_name} to be either int or str, but got {type(key)} for key {key}"
            )
    raise ValueError(
        f"Could not determine key type for records in dataset {dataset_name}."
    )
