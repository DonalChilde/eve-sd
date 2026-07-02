"""Load the SDE dataset records into a sqlite database."""

import logging
import sqlite3
from collections.abc import Iterable
from typing import Any, Literal, cast

from more_itertools import peekable

from eve_static_data.db import models_2 as db_models
from eve_static_data.db.helpers import (
    write_int_records,
    write_key_type,
    write_sde_metadata,
    write_serialization_format,
    write_str_records,
)
from eve_static_data.helpers.sde_metadata import SdeMetadata

logger = logging.getLogger(__name__)


def write_db_metadata(
    connection: sqlite3.Connection,
    *,
    sde_metadata: SdeMetadata,
    serialization_format: db_models.SerializationFormat,
) -> None:
    """Write the SDE metadata to the database."""
    write_sde_metadata(connection, sde_metadata=sde_metadata)
    write_serialization_format(connection, serialization_format=serialization_format)


def get_key_type_from_records(
    *, records: Iterable[tuple[str | int, dict[str | int, Any]]], dataset_name: str
) -> tuple[Literal["int", "str"], Iterable[tuple[str | int, dict[str | int, Any]]]]:
    """Determine the key type of a dataset based on the first record."""
    peekable_records = peekable(records)
    first_record_key, _ = next(peekable_records)
    key_type = type(first_record_key).__name__
    if key_type not in ("int", "str"):
        raise ValueError(
            f"Expected record key in dataset {dataset_name} to be either int or str, but got {key_type} for key {first_record_key}"
        )
    return key_type, peekable_records


def write_sde_records_to_db(
    connection: sqlite3.Connection,
    *,
    records: Iterable[tuple[str | int, dict[str | int, Any]]],
    key_type: Literal["int", "str"],
    dataset_name: str,
    serialization_format: db_models.SerializationFormat,
) -> int:
    """Write SDE records to the database with the specified serialization format."""
    write_key_type(connection, dataset_name=dataset_name, key_type=key_type)
    count: int = 0
    match key_type:
        case "int":
            records = cast(Iterable[tuple[int, dict[str | int, Any]]], records)
            match serialization_format:
                case db_models.SerializationFormat.JSON:
                    record_class = db_models.DatasetRecordIntJson
                case db_models.SerializationFormat.PICKLE:
                    record_class = db_models.DatasetRecordIntPickle
                case db_models.SerializationFormat.YAML:
                    record_class = db_models.DatasetRecordIntYaml
                case _:
                    raise ValueError(
                        f"Unexpected serialization format {serialization_format} for dataset {dataset_name}."
                    )

            def _marshal_int_records(
                record_class: type[db_models.DatasetRecordIntBase],
            ) -> Iterable[db_models.DatasetRecordIntBase]:
                nonlocal count
                for record_key, record in records:
                    count += 1
                    yield record_class.from_record(
                        dataset_name, record_key=record_key, record=record
                    )

            write_int_records(connection, records=_marshal_int_records(record_class))
        case "str":
            records = cast(Iterable[tuple[str, dict[str | int, Any]]], records)
            match serialization_format:
                case db_models.SerializationFormat.JSON:
                    record_class = db_models.DatasetRecordStrJson
                case db_models.SerializationFormat.PICKLE:
                    record_class = db_models.DatasetRecordStrPickle
                case db_models.SerializationFormat.YAML:
                    record_class = db_models.DatasetRecordStrYaml
                case _:
                    raise ValueError(
                        f"Unexpected serialization format {serialization_format} for dataset {dataset_name}."
                    )

            def _marshal_str_records(
                record_class: type[db_models.DatasetRecordStrBase],
            ) -> Iterable[db_models.DatasetRecordStrBase]:
                nonlocal count
                for record_key, record in records:
                    count += 1
                    yield record_class.from_record(
                        dataset_name, record_key=record_key, record=record
                    )

            write_str_records(connection, records=_marshal_str_records(record_class))
        case _:
            raise ValueError(
                f"Unexpected key type {key_type} for dataset {dataset_name}."
            )
    return count


# def _jsonl_key_type(
#     jsonl_record: dict[str, Any], dataset_name: str
# ) -> Literal["int", "str"]:
#     """Helper function to determine the key type of a dataset."""
#     record_key = jsonl_record.get("_key")
#     if isinstance(record_key, int):
#         key_type = "int"
#         return key_type
#     elif isinstance(record_key, str):  # pyright: ignore[reportUnnecessaryIsInstance]
#         key_type = "str"
#         return key_type
#     else:
#         raise ValueError(
#             f"Expected record key in dataset {dataset_name} to be either int or str, but got {type(record_key)} for key {record_key}"
#         )
