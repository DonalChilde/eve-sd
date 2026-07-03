"""Helpers for loading SDE dataset records into SQLite.

This module coordinates metadata writes, record key-type inference, and record
marshalling into database model classes before persistence.
"""

import logging
import sqlite3
from collections.abc import Iterable
from typing import Literal, cast

from more_itertools import peekable

from eve_sd import IntKeyedRecord, KeyedRecord, StrKeyedRecord
from eve_sd.db import models as db_models
from eve_sd.db.helpers import (
    write_int_records,
    write_key_type,
    write_sde_metadata,
    write_serialization_format,
    write_str_records,
)
from eve_sd.helpers.sde_metadata import SdeMetadata

logger = logging.getLogger(__name__)


def write_db_metadata(
    connection: sqlite3.Connection,
    *,
    sde_metadata: SdeMetadata,
    serialization_format: db_models.SerializationFormat,
) -> None:
    """Write SDE metadata and serialization settings to the database.

    Args:
        connection: Open SQLite database connection.
        sde_metadata: Parsed SDE metadata for the imported dataset snapshot.
        serialization_format: Record serialization format stored in the database.
    """
    write_sde_metadata(connection, sde_metadata=sde_metadata)
    write_serialization_format(connection, serialization_format=serialization_format)


def get_key_type_from_records(
    *, records: Iterable[KeyedRecord], dataset_name: str
) -> tuple[Literal["int", "str"], Iterable[KeyedRecord]]:
    """Determine dataset key type from the first record in an iterable.

    Args:
        records: Iterable of keyed records for one dataset.
        dataset_name: Dataset name used in error messages.

    Returns:
        A tuple of ``("int" | "str", records_iterable)``.

    Raises:
        StopIteration: If ``records`` is empty.
        ValueError: If the first record key is not ``int`` or ``str``.

    Notes:
        This function currently does not advance the iterable while
        inspecting the first key.
    """
    peekable_records = peekable(records)
    first_record_key, _ = peekable_records.peek()
    key_type = type(first_record_key).__name__
    if key_type not in ("int", "str"):
        raise ValueError(
            f"Expected record key in dataset {dataset_name} to be either int or str, but got {key_type} for key {first_record_key}"
        )
    return key_type, peekable_records


def write_sde_records_to_db(
    connection: sqlite3.Connection,
    *,
    records: Iterable[KeyedRecord],
    key_type: Literal["int", "str"],
    dataset_name: str,
    serialization_format: db_models.SerializationFormat,
) -> int:
    """Write dataset records to the database using the selected serialization format.

    The function records key-type metadata, marshals records into the
    corresponding database model classes, writes them to the matching table, and
    returns the total written record count.

    Args:
        connection: Open SQLite database connection.
        records: Iterable of dataset records keyed by ``int`` or ``str``.
        key_type: Declared dataset key type.
        dataset_name: Dataset name used for metadata and record storage.
        serialization_format: Serialization format used to encode stored records.

    Returns:
        Number of records written for the dataset.

    Raises:
        ValueError: If ``key_type`` or ``serialization_format`` is unsupported.
    """
    write_key_type(connection, dataset_name=dataset_name, key_type=key_type)
    count: int = 0
    match key_type:
        case "int":
            records = cast(Iterable[IntKeyedRecord], records)
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
                        dataset_name, keyed_record=(record_key, record)
                    )

            write_int_records(connection, records=_marshal_int_records(record_class))
        case "str":
            records = cast(Iterable[StrKeyedRecord], records)
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
                        dataset_name, keyed_record=(record_key, record)
                    )

            write_str_records(connection, records=_marshal_str_records(record_class))
        case _:
            raise ValueError(
                f"Unexpected key type {key_type} for dataset {dataset_name}."
            )
    return count
