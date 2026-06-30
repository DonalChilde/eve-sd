"""Load the SDE datasets from JSONL files into a sqlite database."""

import logging
import sqlite3
from pathlib import Path
from typing import Any, Literal

from more_itertools import peekable
from pydantic_core import from_json

from eve_static_data.db import models_2 as db_models
from eve_static_data.db.helpers import (
    write_int_records,
    write_key_type,
    write_sde_metadata,
    write_str_records,
)
from eve_static_data.helpers.sde_metadata import load_sde_metadata

logger = logging.getLogger(__name__)


def import_jsonl_sde_to_db(
    sde_path: Path,
    *,
    connection: sqlite3.Connection,
    serialization_format: db_models.SerializationFormat = db_models.SerializationFormat.JSON,
) -> None:
    """Load JSONL SDE datasets into sqlite and serialize each record as bytes.

    This loader reads the dataset JSONL files and the `_sde.jsonl` metadata file from
    ``sde_path``, then stores the parsed records in the provided sqlite connection.
    The chosen ``serialization_format`` only affects how each record payload is stored
    in the database after parsing.

    Format tradeoffs:
    - ``YAML`` keeps the stored payload human-readable and can preserve the original
        mapping shape more naturally, but it is slower to serialize and deserialize.
    - ``JSON`` is widely interoperable and compact.
    - ``PICKLE`` is usually the fastest option and round-trips Python objects most
        faithfully, but it is Python-specific, not human-readable, and should only be
        used with trusted data.

    The loader expects the input directory to contain JSONL files for each dataset and
    a ``_sde.jsonl`` metadata file.

    Args:
            sde_path: Directory containing the JSONL datasets to import.
            connection: Open sqlite connection that receives the imported rows.
            serialization_format: Byte format used to store each record in the database.
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
            key_type = _jsonl_key_type(first_record, dataset_name)
            write_key_type(
                connection,
                dataset_name=dataset_name,
                key_type=key_type,
                serialization_format=serialization_format,
            )
            match key_type:
                case "int":
                    match serialization_format:
                        case db_models.SerializationFormat.JSON:
                            record_class = db_models.DatasetRecordIntJson
                        case db_models.SerializationFormat.PICKLE:
                            record_class = db_models.DatasetRecordIntPickle
                        case db_models.SerializationFormat.YAML:
                            record_class = db_models.DatasetRecordIntYaml
                        case _:
                            raise ValueError(
                                f"Unexpected serialization format {serialization_format} for dataset {dataset_name} in {jsonl_file}."
                            )
                    records = (
                        record_class.from_record(
                            dataset_name, record_key=record["_key"], record=record
                        )
                        for record in peekable_records
                    )
                    write_int_records(connection, records=records)
                case "str":
                    match serialization_format:
                        case db_models.SerializationFormat.JSON:
                            record_class = db_models.DatasetRecordStrJson
                        case db_models.SerializationFormat.PICKLE:
                            record_class = db_models.DatasetRecordStrPickle
                        case db_models.SerializationFormat.YAML:
                            record_class = db_models.DatasetRecordStrYaml
                        case _:
                            raise ValueError(
                                f"Unexpected serialization format {serialization_format} for dataset {dataset_name} in {jsonl_file}."
                            )
                    records = (
                        record_class.from_record(
                            dataset_name, record_key=record["_key"], record=record
                        )
                        for record in peekable_records
                    )
                    write_str_records(connection, records=records)
                case _:
                    raise ValueError(
                        f"Unexpected key type {key_type} for dataset {dataset_name} in {jsonl_file}."
                    )


def _jsonl_key_type(
    jsonl_record: dict[str, Any], dataset_name: str
) -> Literal["int", "str"]:
    """Helper function to determine the key type of a dataset."""
    record_key = jsonl_record.get("_key")
    if isinstance(record_key, int):
        key_type = "int"
        return key_type
    elif isinstance(record_key, str):  # pyright: ignore[reportUnnecessaryIsInstance]
        key_type = "str"
        return key_type
    else:
        raise ValueError(
            f"Expected record key in dataset {dataset_name} to be either int or str, but got {type(record_key)} for key {record_key}"
        )
