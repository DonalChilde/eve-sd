"""Helper functions for database operations."""

import logging
import sqlite3
from collections.abc import Iterable
from contextlib import contextmanager
from importlib.resources import files as resource_files
from typing import Any
from uuid import uuid4

from eve_static_data.db.primary.models import DatasetRecordInt, DatasetRecordStr
from eve_static_data.helpers.sde_metadata import SdeMetadata

logger = logging.getLogger(__name__)

_table_def_parent = "eve_static_data.db.primary"
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
    records: Iterable[DatasetRecordInt],
) -> dict[str, dict[int, Any]]:
    """Deserialize an iterable of DatasetRecordInt instances into a nested dictionary."""
    result: dict[str, dict[int, Any]] = {}
    for record in records:
        if record.dataset_name not in result:
            result[record.dataset_name] = {}
        result[record.dataset_name][record.record_key] = record.deserialize_record()
    return result


def deserialize_str_records(
    records: Iterable[DatasetRecordStr],
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
    records: Iterable[DatasetRecordInt],
    *,
    connection: sqlite3.Connection,
) -> None:
    """Write an interable of DatasetRecordInt instances to the database."""
    with transaction(connection):
        connection.executemany(
            """
                INSERT INTO DatasetRecordsInt (record_key, dataset_name, record_json)
                VALUES (?, ?, ?)
                ON CONFLICT(record_key, dataset_name) DO UPDATE SET record_json=excluded.record_json
                """,
            (
                (record.record_key, record.dataset_name, record.record_json)
                for record in records
            ),
        )


def write_str_records(
    records: Iterable[DatasetRecordStr],
    *,
    connection: sqlite3.Connection,
) -> None:
    """Write an interable of DatasetRecordStr instances to the database."""
    with transaction(connection):
        connection.executemany(
            """
                INSERT INTO DatasetRecordsStr (record_key, dataset_name, record_json)
                VALUES (?, ?, ?)
                ON CONFLICT(record_key, dataset_name) DO UPDATE SET record_json=excluded.record_json
                """,
            (
                (record.record_key, record.dataset_name, record.record_json)
                for record in records
            ),
        )


def write_key_type(conn: sqlite3.Connection, dataset_name: str, key_type: str) -> None:
    """Write the key type for a dataset to the database."""
    if key_type not in ("int", "str"):
        raise ValueError("key_type must be either 'int' or 'str'.")
    with transaction(conn):
        conn.execute(
            """
                INSERT INTO DatasetKeyType (dataset_name, key_type)
                VALUES (?, ?)
                ON CONFLICT(dataset_name) DO UPDATE SET key_type=excluded.key_type
                """,
            (dataset_name, key_type),
        )


def read_key_types(conn: sqlite3.Connection) -> dict[str, str]:
    """Read all dataset key types from the database."""
    with transaction(conn):
        cursor = conn.execute("SELECT dataset_name, key_type FROM DatasetKeyType")
        return {row["dataset_name"]: row["key_type"] for row in cursor}


def read_int_keys(conn: sqlite3.Connection, dataset_name: str) -> set[int]:
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


def read_str_keys(conn: sqlite3.Connection, dataset_name: str) -> set[str]:
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


def read_int_records(
    conn: sqlite3.Connection, dataset_name: str, record_keys: set[int] | None = None
) -> Iterable[DatasetRecordInt]:
    """Read all records for a dataset with integer keys from the database.

    If record_keys is provided, only return records with keys in the set.
    If record_keys is None, return all records for the dataset.
    If record_keys is provided and has fewer than 500 keys, use a simple IN query.
    If record_keys is provided and has 500 or more keys, create a temporary table and join against it.
    """
    if record_keys is None:
        with transaction(conn):
            cursor = conn.execute(
                """
                    SELECT record_key, dataset_name, record_json
                    FROM DatasetRecordsInt
                    WHERE dataset_name = ?
                    """,
                (dataset_name,),
            )
            for row in cursor:
                yield DatasetRecordInt(
                    record_key=row["record_key"],
                    dataset_name=row["dataset_name"],
                    record_json=row["record_json"],
                )
    elif len(record_keys) < 500:
        with transaction(conn):
            cursor = conn.execute(
                f"""
                    SELECT record_key, dataset_name, record_json
                    FROM DatasetRecordsInt
                    WHERE dataset_name = ?
                    AND record_key IN ({",".join("?" for _ in record_keys)})
                    """,
                (dataset_name, *record_keys),
            )
            for row in cursor:
                yield DatasetRecordInt(
                    record_key=row["record_key"],
                    dataset_name=row["dataset_name"],
                    record_json=row["record_json"],
                )
    else:
        table_name = f"temp_keys_{uuid4().hex}"
        with transaction(conn) as conn:
            conn.execute(
                f"""
                    CREATE TEMPORARY TABLE {table_name} (
                        record_key INTEGER PRIMARY KEY
                    )
                    """,
            )
            conn.executemany(
                f"""
                    INSERT INTO {table_name} (record_key) VALUES (?)
                    """,
                ((key,) for key in record_keys),
            )
            cursor = conn.execute(
                f"""
                    SELECT r.record_key, r.dataset_name, r.record_json
                    FROM DatasetRecordsInt r
                    JOIN {table_name} k ON r.record_key = k.record_key
                    WHERE r.dataset_name = ?
                    """,
                (dataset_name,),
            )
            for row in cursor:
                yield DatasetRecordInt(
                    record_key=row["record_key"],
                    dataset_name=row["dataset_name"],
                    record_json=row["record_json"],
                )
            conn.execute(f"DROP TABLE {table_name}")


def read_str_records(
    conn: sqlite3.Connection, dataset_name: str, record_keys: set[str] | None = None
) -> Iterable[DatasetRecordStr]:
    """Read all records for a dataset with string keys from the database.

    If record_keys is provided, only return records with keys in the set.
    If record_keys is None, return all records for the dataset.
    If record_keys is provided and has fewer than 500 keys, use a simple IN query.
    If record_keys is provided and has 500 or more keys, create a temporary table and join against it.
    """
    if record_keys is None:
        with transaction(conn):
            cursor = conn.execute(
                """
                    SELECT record_key, dataset_name, record_json
                    FROM DatasetRecordsStr
                    WHERE dataset_name = ?
                    """,
                (dataset_name,),
            )
            for row in cursor:
                yield DatasetRecordStr(
                    record_key=row["record_key"],
                    dataset_name=row["dataset_name"],
                    record_json=row["record_json"],
                )
    elif len(record_keys) < 500:
        with transaction(conn):
            cursor = conn.execute(
                f"""
                    SELECT record_key, dataset_name, record_json
                    FROM DatasetRecordsStr
                    WHERE dataset_name = ?
                    AND record_key IN ({",".join("?" for _ in record_keys)})
                    """,
                (dataset_name, *record_keys),
            )
            for row in cursor:
                yield DatasetRecordStr(
                    record_key=row["record_key"],
                    dataset_name=row["dataset_name"],
                    record_json=row["record_json"],
                )
    else:
        table_name = f"temp_keys_{uuid4().hex}"
        with transaction(conn) as conn:
            conn.execute(
                f"""
                    CREATE TEMPORARY TABLE {table_name} (
                        record_key TEXT PRIMARY KEY
                    )
                    """,
            )
            conn.executemany(
                f"""
                    INSERT INTO {table_name} (record_key) VALUES (?)
                    """,
                ((key,) for key in record_keys),
            )
            cursor = conn.execute(
                f"""
                    SELECT r.record_key, r.dataset_name, r.record_json
                    FROM DatasetRecordsStr r
                    JOIN {table_name} k ON r.record_key = k.record_key
                    WHERE r.dataset_name = ?
                    """,
                (dataset_name,),
            )
            for row in cursor:
                yield DatasetRecordStr(
                    record_key=row["record_key"],
                    dataset_name=row["dataset_name"],
                    record_json=row["record_json"],
                )
            conn.execute(f"DROP TABLE {table_name}")


def write_sde_metadata(conn: sqlite3.Connection, sde_metadata: SdeMetadata) -> None:
    """Write the SDE metadata to the database."""
    if sde_metadata.source_format is None:
        raise ValueError("source_format must be provided in sde_metadata.")
    with transaction(conn):
        conn.execute(
            """
                INSERT INTO SdeMetadata (buildNumber, releaseDate, source_format)
                VALUES (?, ?, ?)
                ON CONFLICT(buildNumber) DO UPDATE SET releaseDate=excluded.releaseDate, source_format=excluded.source_format
                """,
            (
                sde_metadata.buildNumber,
                sde_metadata.releaseDate,
                sde_metadata.source_format,
            ),
        )
