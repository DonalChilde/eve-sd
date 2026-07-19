"""Tests for eve_sd.db.helpers — connections, transactions, writes, and queries."""

import sqlite3
from pathlib import Path

import pytest

from pfmsoft.eve_sd.db.helpers import (
    create_read_write_connection,
    query_dataset_record_count,
    query_int_keys,
    query_key_types,
    query_sde_metadata,
    query_str_keys,
    read_only_uri,
    read_write_uri,
    transaction,
    write_int_records,
    write_key_type,
    write_key_types,
    write_sde_metadata,
    write_serialization_format,
    write_str_records,
)
from pfmsoft.eve_sd.db.models import (
    DatasetRecordIntJson,
    DatasetRecordStrJson,
    SerializationFormat,
)
from pfmsoft.eve_sd.helpers.sde_metadata import SdeMetadata, SdeVariant, SourceMedia

# ---------------------------------------------------------------------------
# URI helpers
# ---------------------------------------------------------------------------


class TestUriHelpers:
    """Tests for read_only_uri and read_write_uri."""

    def test_read_only_uri_contains_mode_ro(self) -> None:
        """read_only_uri embeds mode=ro."""
        uri = read_only_uri("/tmp/test.db")
        assert "mode=ro" in uri

    def test_read_write_uri_contains_mode_rwc(self) -> None:
        """read_write_uri embeds mode=rwc."""
        uri = read_write_uri("/tmp/test.db")
        assert "mode=rwc" in uri

    def test_uri_includes_path(self) -> None:
        """Both URI helpers include the original path."""
        path = "/some/path/to/db.sqlite"
        assert path in read_only_uri(path)
        assert path in read_write_uri(path)


# ---------------------------------------------------------------------------
# Connection creation
# ---------------------------------------------------------------------------


class TestCreateReadWriteConnection:
    """Tests for create_read_write_connection."""

    def test_returns_sqlite_connection(self, tmp_path: Path) -> None:
        """create_read_write_connection returns a sqlite3.Connection."""
        db_path = str(tmp_path / "test.db")
        conn = create_read_write_connection(db_path)
        assert isinstance(conn, sqlite3.Connection)
        conn.close()

    def test_schema_tables_exist(self, tmp_path: Path) -> None:
        """Core schema tables are present after bootstrapping."""
        db_path = str(tmp_path / "test.db")
        conn = create_read_write_connection(db_path)
        tables = {
            row[0]
            for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
        assert "DatasetRecordsInt" in tables
        assert "DatasetRecordsStr" in tables
        conn.close()

    def test_creates_db_file_on_disk(self, tmp_path: Path) -> None:
        """The database file is created on disk."""
        db_path = tmp_path / "new.db"
        conn = create_read_write_connection(str(db_path))
        conn.close()
        assert db_path.exists()


# ---------------------------------------------------------------------------
# Transaction context manager
# ---------------------------------------------------------------------------


class TestTransaction:
    """Tests for the transaction context manager."""

    def test_commits_on_clean_exit(self, rw_connection: sqlite3.Connection) -> None:
        """Data written inside a transaction block is committed on success."""
        with transaction(rw_connection):
            rw_connection.execute(
                "INSERT INTO DatasetRecordsInt (record_key, dataset_name, record_bytes) VALUES (1, 'ds', ?)",
                (b"data",),
            )
        count = rw_connection.execute(
            "SELECT COUNT(*) FROM DatasetRecordsInt WHERE dataset_name='ds'"
        ).fetchone()[0]
        assert count == 1

    def test_rolls_back_on_exception(self, rw_connection: sqlite3.Connection) -> None:
        """Data written inside a failing transaction block is rolled back."""
        with pytest.raises(RuntimeError):
            with transaction(rw_connection):
                rw_connection.execute(
                    "INSERT INTO DatasetRecordsInt (record_key, dataset_name, record_bytes) VALUES (99, 'rollback_ds', ?)",
                    (b"data",),
                )
                raise RuntimeError("intentional failure")
        count = rw_connection.execute(
            "SELECT COUNT(*) FROM DatasetRecordsInt WHERE dataset_name='rollback_ds'"
        ).fetchone()[0]
        assert count == 0


# ---------------------------------------------------------------------------
# Write helpers
# ---------------------------------------------------------------------------


class TestWriteIntRecords:
    """Tests for write_int_records."""

    def test_writes_records_to_database(
        self,
        rw_connection: sqlite3.Connection,
        sample_int_records: list[tuple[int, dict]],
    ) -> None:
        """Integer-keyed records are persisted in DatasetRecordsInt."""
        db_records = [
            DatasetRecordIntJson.from_record("agents", r) for r in sample_int_records
        ]
        write_int_records(rw_connection, records=db_records)
        count = rw_connection.execute(
            "SELECT COUNT(*) FROM DatasetRecordsInt WHERE dataset_name='agents'"
        ).fetchone()[0]
        assert count == 3

    def test_upsert_replaces_existing_record(
        self, rw_connection: sqlite3.Connection
    ) -> None:
        """Writing the same key twice keeps only the latest value."""
        record_v1 = DatasetRecordIntJson.from_record(
            "ds", (1, {"_key": 1, "v": "first"})
        )
        record_v2 = DatasetRecordIntJson.from_record(
            "ds", (1, {"_key": 1, "v": "second"})
        )
        write_int_records(rw_connection, records=[record_v1])
        write_int_records(rw_connection, records=[record_v2])
        count = rw_connection.execute(
            "SELECT COUNT(*) FROM DatasetRecordsInt WHERE dataset_name='ds'"
        ).fetchone()[0]
        assert count == 1


class TestWriteStrRecords:
    """Tests for write_str_records."""

    def test_writes_records_to_database(
        self,
        rw_connection: sqlite3.Connection,
        sample_str_records: list[tuple[str, dict]],
    ) -> None:
        """String-keyed records are persisted in DatasetRecordsStr."""
        db_records = [
            DatasetRecordStrJson.from_record("sde_meta", r) for r in sample_str_records
        ]
        write_str_records(rw_connection, records=db_records)
        count = rw_connection.execute(
            "SELECT COUNT(*) FROM DatasetRecordsStr WHERE dataset_name='sde_meta'"
        ).fetchone()[0]
        assert count == 2


# ---------------------------------------------------------------------------
# Metadata and settings writes
# ---------------------------------------------------------------------------


class TestWriteSdeMetadata:
    """Tests for write_sde_metadata and query_sde_metadata."""

    def test_metadata_round_trip(
        self,
        rw_connection: sqlite3.Connection,
        sample_metadata: SdeMetadata,
    ) -> None:
        """Metadata written is retrievable via query_sde_metadata."""
        write_sde_metadata(rw_connection, sde_metadata=sample_metadata)
        result = query_sde_metadata(rw_connection)
        assert result is not None
        assert result.buildNumber == sample_metadata.buildNumber
        assert result.releaseDate == sample_metadata.releaseDate

    def test_query_sde_metadata_returns_none_when_empty(
        self, rw_connection: sqlite3.Connection
    ) -> None:
        """query_sde_metadata returns None on an empty database."""
        result = query_sde_metadata(rw_connection)
        assert result is None


class TestWriteSerializationFormat:
    """Tests for write_serialization_format."""

    def test_serialization_format_persisted(
        self, rw_connection: sqlite3.Connection
    ) -> None:
        """write_serialization_format stores the format in DatabaseSettings."""
        write_serialization_format(
            rw_connection, serialization_format=SerializationFormat.JSON
        )
        row = rw_connection.execute(
            "SELECT serialization_format FROM DatabaseSettings"
        ).fetchone()
        assert row is not None
        assert row[0] == "json"


# ---------------------------------------------------------------------------
# Key type writes and queries
# ---------------------------------------------------------------------------


class TestKeyTypes:
    """Tests for write_key_type, write_key_types, and query_key_types."""

    def test_write_and_query_single_key_type(
        self, rw_connection: sqlite3.Connection
    ) -> None:
        """A single key-type entry survives a write/query round-trip."""
        write_key_type(rw_connection, dataset_name="categories", key_type="int")
        key_types = query_key_types(rw_connection)
        assert key_types["categories"] == "int"

    def test_write_and_query_multiple_key_types(
        self, rw_connection: sqlite3.Connection
    ) -> None:
        """Multiple key-type entries are all retrievable."""
        write_key_types(
            rw_connection,
            dataset_key_types={"alpha": "str", "beta": "int"},
        )
        key_types = query_key_types(rw_connection)
        assert key_types["alpha"] == "str"
        assert key_types["beta"] == "int"


# ---------------------------------------------------------------------------
# Record count and key queries
# ---------------------------------------------------------------------------


class TestQueryHelpers:
    """Tests for query_int_keys, query_str_keys, and query_dataset_record_count."""

    def test_query_int_keys_returns_set(
        self,
        rw_connection: sqlite3.Connection,
        sample_int_records: list[tuple[int, dict]],
    ) -> None:
        """query_int_keys returns the set of stored integer keys."""
        db_records = [
            DatasetRecordIntJson.from_record("agents", r) for r in sample_int_records
        ]
        write_int_records(rw_connection, records=db_records)
        keys = query_int_keys(rw_connection, dataset_name="agents")
        assert keys == {1, 2, 3}

    def test_query_str_keys_returns_set(
        self,
        rw_connection: sqlite3.Connection,
        sample_str_records: list[tuple[str, dict]],
    ) -> None:
        """query_str_keys returns the set of stored string keys."""
        db_records = [
            DatasetRecordStrJson.from_record("sde_meta", r) for r in sample_str_records
        ]
        write_str_records(rw_connection, records=db_records)
        keys = query_str_keys(rw_connection, dataset_name="sde_meta")
        assert keys == {"sde", "meta"}

    def test_query_dataset_record_count_int(
        self,
        rw_connection: sqlite3.Connection,
        sample_int_records: list[tuple[int, dict]],
    ) -> None:
        """query_dataset_record_count returns the correct count for int-keyed records."""
        db_records = [
            DatasetRecordIntJson.from_record("agents", r) for r in sample_int_records
        ]
        write_int_records(rw_connection, records=db_records)
        count = query_dataset_record_count(
            rw_connection, dataset_name="agents", key_type="int"
        )
        assert count == 3

    def test_query_dataset_record_count_str(
        self,
        rw_connection: sqlite3.Connection,
        sample_str_records: list[tuple[str, dict]],
    ) -> None:
        """query_dataset_record_count returns the correct count for str-keyed records."""
        db_records = [
            DatasetRecordStrJson.from_record("sde_meta", r) for r in sample_str_records
        ]
        write_str_records(rw_connection, records=db_records)
        count = query_dataset_record_count(
            rw_connection, dataset_name="sde_meta", key_type="str"
        )
        assert count == 2

    def test_record_count_zero_for_unknown_dataset(
        self, rw_connection: sqlite3.Connection
    ) -> None:
        """query_dataset_record_count returns 0 for a dataset with no records."""
        count = query_dataset_record_count(
            rw_connection, dataset_name="nonexistent", key_type="int"
        )
        assert count == 0
