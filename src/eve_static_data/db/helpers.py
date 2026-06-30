"""Helper functions for database operations."""

import logging
import sqlite3
from collections.abc import Iterable
from contextlib import contextmanager
from importlib.resources import files as resource_files
from typing import Any
from uuid import uuid4

from eve_static_data.db import models_2 as db_models
from eve_static_data.helpers.sde_metadata import SdeMetadata

logger = logging.getLogger(__name__)

_table_def_parent = "eve_static_data.db"
_table_def_sql = "table_defs.sql"


@contextmanager
def transaction(conn: sqlite3.Connection):
    """Wrap a block in an explicit transaction.

    Commits on clean exit, rolls back on any exception.

    sqlite3.connect() has autocommit behaviour that changed in 3.12 and was
    further clarified in 3.14 (PEP 249-compliant isolation_level=None gives
    you a pure manual-commit mode). Using an explicit context manager here
    keeps intent clear regardless of the default.
    """
    try:
        conn.execute("BEGIN")
        yield conn
        conn.execute("COMMIT")
    except Exception as e:
        logger.error("Transaction failed. %s", e, exc_info=e)
        conn.execute("ROLLBACK")
        raise


def deserialize_int_records(
    records: Iterable[db_models.DatasetRecordIntBase],
) -> dict[str, dict[int, Any]]:
    """Deserialize an iterable of DatasetRecordInt instances into a nested dictionary."""
    result: dict[str, dict[int, Any]] = {}
    for record in records:
        if record.dataset_name not in result:
            result[record.dataset_name] = {}
        result[record.dataset_name][record.record_key] = record.deserialize_record()
    return result


def deserialize_str_records(
    records: Iterable[db_models.DatasetRecordStrBase],
) -> dict[str, dict[str, Any]]:
    """Deserialize an iterable of DatasetRecordStr instances into a nested dictionary."""
    result: dict[str, dict[str, Any]] = {}
    for record in records:
        if record.dataset_name not in result:
            result[record.dataset_name] = {}
        result[record.dataset_name][record.record_key] = record.deserialize_record()
    return result


def read_only_uri(db_path: str) -> str:
    """Construct a read-only URI for the given database path."""
    return f"file:{db_path}?mode=ro"


def read_write_uri(db_path: str) -> str:
    """Construct a read-write URI for the given database path."""
    return f"file:{db_path}?mode=rwc"


def create_read_only_connection(db_path: str) -> sqlite3.Connection:
    """Create a read-only connection to the database at the given path."""
    uri = read_only_uri(db_path)
    connection = sqlite3.connect(uri, uri=True)
    connection.row_factory = sqlite3.Row
    table_defs = resource_files(_table_def_parent).joinpath(_table_def_sql).read_text()
    with transaction(connection) as conn:
        conn.executescript(table_defs)
    return connection


def create_read_write_connection(db_path: str) -> sqlite3.Connection:
    """Create a read-write connection to the database at the given path."""
    uri = read_write_uri(db_path)
    # Use the transaction context manager.
    connection = sqlite3.connect(uri, uri=True, autocommit=True)
    logger.info(f"Created read-write connection to database at {db_path}")
    connection.row_factory = sqlite3.Row
    table_defs = resource_files(_table_def_parent).joinpath(_table_def_sql).read_text()
    with transaction(connection) as conn:
        conn.executescript(table_defs)
        logger.info("Ensured database schema is created.")
    return connection


def write_int_records(
    connection: sqlite3.Connection,
    *,
    records: Iterable[db_models.DatasetRecordIntBase],
) -> None:
    """Write an interable of DatasetRecordInt instances to the database."""
    with transaction(connection):
        connection.executemany(
            """
                INSERT INTO DatasetRecordsInt (record_key, dataset_name, record_bytes)
                VALUES (?, ?, ?)
                ON CONFLICT(record_key, dataset_name) DO UPDATE SET record_bytes=excluded.record_bytes
                """,
            (
                (record.record_key, record.dataset_name, record.record)
                for record in records
            ),
        )


def write_str_records(
    connection: sqlite3.Connection,
    *,
    records: Iterable[db_models.DatasetRecordStrBase],
) -> None:
    """Write an interable of DatasetRecordStr instances to the database."""
    with transaction(connection):
        connection.executemany(
            """
                INSERT INTO DatasetRecordsStr (record_key, dataset_name, record_bytes)
                VALUES (?, ?, ?)
                ON CONFLICT(record_key, dataset_name) DO UPDATE SET record_bytes=excluded.record_bytes
                """,
            (
                (record.record_key, record.dataset_name, record.record)
                for record in records
            ),
        )


# TODO Standardize function sigs like this one.
def write_key_type(
    connection: sqlite3.Connection,
    *,
    dataset_name: str,
    key_type: str,
    serialization_format: db_models.SerializationFormat,
) -> None:
    """Write the key type for a dataset to the database."""
    if key_type not in ("int", "str"):
        raise ValueError("key_type must be either 'int' or 'str'.")
    with transaction(connection):
        connection.execute(
            """
                INSERT INTO DatasetKeyType (dataset_name, key_type, serialization_format)
                VALUES (?, ?, ?)
                ON CONFLICT(dataset_name) DO UPDATE SET key_type=excluded.key_type, serialization_format=excluded.serialization_format
                """,
            (dataset_name, key_type, serialization_format.value),
        )


def write_serialization_format(
    connection: sqlite3.Connection,
    *,
    serialization_format: db_models.SerializationFormat,
) -> None:
    """Write the serialization format to the DatabaseSettings table."""
    with transaction(connection):
        connection.execute(
            """
                INSERT INTO DatabaseSettings (row_id, serialization_format)
                VALUES (1, ?)
                ON CONFLICT(row_id) DO UPDATE SET serialization_format=excluded.serialization_format
                """,
            (serialization_format.value,),
        )


def query_key_types(connection: sqlite3.Connection) -> dict[str, str]:
    """Read all dataset key types from the database."""
    with transaction(connection):
        cursor = connection.execute("SELECT dataset_name, key_type FROM DatasetKeyType")
        return {row["dataset_name"]: row["key_type"] for row in cursor}


def query_database_settings(connection: sqlite3.Connection) -> dict[str, Any]:
    """Read the database settings from the DatabaseSettings table."""
    with transaction(connection):
        cursor = connection.execute(
            "SELECT serialization_format FROM DatabaseSettings WHERE row_id = 1"
        )
        row = cursor.fetchone()
        if row is None:
            return {}
        return {"serialization_format": row["serialization_format"]}


def query_int_keys(conn: sqlite3.Connection, dataset_name: str) -> set[int]:
    """Read all integer keys for a dataset from the database."""
    with transaction(conn):
        cursor = conn.execute(
            """
                SELECT record_key
                FROM DatasetRecordsInt
                WHERE dataset_name = ?
                """,
            (dataset_name,),
        )
        return {row["record_key"] for row in cursor}


def query_str_keys(conn: sqlite3.Connection, dataset_name: str) -> set[str]:
    """Read all string keys for a dataset from the database."""
    with transaction(conn):
        cursor = conn.execute(
            """
                SELECT record_key
                FROM DatasetRecordsStr
                WHERE dataset_name = ?
                """,
            (dataset_name,),
        )
        return {row["record_key"] for row in cursor}


def query_int_records(
    connection: sqlite3.Connection,
    *,
    dataset_name: str,
    serialization_format: db_models.SerializationFormat,
    record_keys: set[int] | None = None,
) -> Iterable[db_models.DatasetRecordIntBase]:
    """Read all records for a dataset with integer keys from the database.

    If record_keys is provided, only return records with keys in the set.
    If record_keys is None, return all records for the dataset.
    If record_keys is provided and has fewer than 500 keys, use a simple IN query.
    If record_keys is provided and has 500 or more keys, create a temporary table and join against it.
    """
    match serialization_format:
        case db_models.SerializationFormat.YAML:
            record_class = db_models.DatasetRecordIntYaml
        case db_models.SerializationFormat.JSON:
            record_class = db_models.DatasetRecordIntJson
        case db_models.SerializationFormat.PICKLE:
            record_class = db_models.DatasetRecordIntPickle
        case _:
            raise ValueError(
                f"Unsupported serialization format: {serialization_format}. Must be one of 'yaml', 'json', or 'pickle'."
            )
    if record_keys is None:
        with transaction(connection):
            cursor = connection.execute(
                """
                    SELECT record_key, dataset_name, record_bytes
                    FROM DatasetRecordsInt
                    WHERE dataset_name = ?
                    """,
                (dataset_name,),
            )
            for row in cursor:
                yield record_class(
                    record_key=row["record_key"],
                    dataset_name=row["dataset_name"],
                    record=row["record_bytes"],
                )
    elif len(record_keys) < 500:
        with transaction(connection):
            cursor = connection.execute(
                f"""
                    SELECT record_key, dataset_name, record_bytes
                    FROM DatasetRecordsInt
                    WHERE dataset_name = ?
                    AND record_key IN ({",".join("?" for _ in record_keys)})
                    """,
                (dataset_name, *record_keys),
            )
            for row in cursor:
                yield record_class(
                    record_key=row["record_key"],
                    dataset_name=row["dataset_name"],
                    record=row["record_bytes"],
                )
    else:
        table_name = f"temp_keys_{uuid4().hex}"
        with transaction(connection) as connection:
            connection.execute(
                f"""
                    CREATE TEMPORARY TABLE {table_name} (
                        record_key INTEGER PRIMARY KEY
                    )
                    """,
            )
            connection.executemany(
                f"""
                    INSERT INTO {table_name} (record_key) VALUES (?)
                    """,
                ((key,) for key in record_keys),
            )
            cursor = connection.execute(
                f"""
                    SELECT r.record_key, r.dataset_name, r.record_bytes
                    FROM DatasetRecordsInt r
                    JOIN {table_name} k ON r.record_key = k.record_key
                    WHERE r.dataset_name = ?
                    """,
                (dataset_name,),
            )
            for row in cursor:
                yield record_class(
                    record_key=row["record_key"],
                    dataset_name=row["dataset_name"],
                    record=row["record_bytes"],
                )
            connection.execute(f"DROP TABLE {table_name}")


def query_str_records(
    connection: sqlite3.Connection,
    *,
    dataset_name: str,
    serialization_format: db_models.SerializationFormat,
    record_keys: set[str] | None = None,
) -> Iterable[db_models.DatasetRecordStrBase]:
    """Read all records for a dataset with string keys from the database.

    If record_keys is provided, only return records with keys in the set.
    If record_keys is None, return all records for the dataset.
    If record_keys is provided and has fewer than 500 keys, use a simple IN query.
    If record_keys is provided and has 500 or more keys, create a temporary table and join against it.
    """
    match serialization_format:
        case db_models.SerializationFormat.YAML:
            record_class = db_models.DatasetRecordStrYaml
        case db_models.SerializationFormat.JSON:
            record_class = db_models.DatasetRecordStrJson
        case db_models.SerializationFormat.PICKLE:
            record_class = db_models.DatasetRecordStrPickle
        case _:
            raise ValueError(
                f"Unsupported serialization format: {serialization_format}. Must be one of 'yaml', 'json', or 'pickle'."
            )
    if record_keys is None:
        with transaction(connection):
            cursor = connection.execute(
                """
                    SELECT record_key, dataset_name, record_bytes
                    FROM DatasetRecordsStr
                    WHERE dataset_name = ?
                    """,
                (dataset_name,),
            )
            for row in cursor:
                yield record_class(
                    record_key=row["record_key"],
                    dataset_name=row["dataset_name"],
                    record=row["record_bytes"],
                )
    elif len(record_keys) < 500:
        with transaction(connection):
            cursor = connection.execute(
                f"""
                    SELECT record_key, dataset_name, record_bytes
                    FROM DatasetRecordsStr
                    WHERE dataset_name = ?
                    AND record_key IN ({",".join("?" for _ in record_keys)})
                    """,
                (dataset_name, *record_keys),
            )
            for row in cursor:
                yield record_class(
                    record_key=row["record_key"],
                    dataset_name=row["dataset_name"],
                    record=row["record_bytes"],
                )
    else:
        table_name = f"temp_keys_{uuid4().hex}"
        with transaction(connection) as connection:
            connection.execute(
                f"""
                    CREATE TEMPORARY TABLE {table_name} (
                        record_key TEXT PRIMARY KEY
                    )
                    """,
            )
            connection.executemany(
                f"""
                    INSERT INTO {table_name} (record_key) VALUES (?)
                    """,
                ((key,) for key in record_keys),
            )
            cursor = connection.execute(
                f"""
                    SELECT r.record_key, r.dataset_name, r.record_bytes
                    FROM DatasetRecordsStr r
                    JOIN {table_name} k ON r.record_key = k.record_key
                    WHERE r.dataset_name = ?
                    """,
                (dataset_name,),
            )
            for row in cursor:
                yield record_class(
                    record_key=row["record_key"],
                    dataset_name=row["dataset_name"],
                    record=row["record_bytes"],
                )
            connection.execute(f"DROP TABLE {table_name}")


def write_sde_metadata(conn: sqlite3.Connection, sde_metadata: SdeMetadata) -> None:
    """Write the SDE metadata to the database."""
    with transaction(conn):
        conn.execute(
            """
                INSERT INTO SdeMetadata (buildNumber, releaseDate, source_format, source_media)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(buildNumber) DO UPDATE SET releaseDate=excluded.releaseDate, source_format=excluded.source_format, source_media=excluded.source_media
                """,
            (
                sde_metadata.buildNumber,
                sde_metadata.releaseDate,
                sde_metadata.source_format,
                ".db",
            ),
        )


def query_sde_metadata(conn: sqlite3.Connection) -> SdeMetadata | None:
    """Query the SDE metadata from the database."""
    with transaction(conn):
        cursor = conn.execute(
            """
                SELECT buildNumber, releaseDate, source_format, source_media
                FROM SdeMetadata
                ORDER BY row_id DESC
                LIMIT 1
                """
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return SdeMetadata(
            buildNumber=row["buildNumber"],
            releaseDate=row["releaseDate"],
            source_format=row["source_format"],
            source_media=row["source_media"],
        )
