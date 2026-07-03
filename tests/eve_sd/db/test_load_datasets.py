"""Tests for eve_sd.db.load_datasets."""

import sqlite3

import pytest

from eve_sd.db.load_datasets import (
    get_key_type_from_records,
    write_db_metadata,
    write_sde_records_to_db,
)
from eve_sd.db.models import SerializationFormat
from eve_sd.db.helpers import query_key_types, query_sde_metadata
from eve_sd.helpers.sde_metadata import SdeMetadata, SdeVariant, SourceMedia


class TestGetKeyTypeFromRecords:
    """Tests for get_key_type_from_records."""

    def test_detects_int_key_type(self) -> None:
        """Returns 'int' when the first record key is an integer."""
        records = [(1, {"_key": 1}), (2, {"_key": 2})]
        key_type, _ = get_key_type_from_records(
            records=iter(records), dataset_name="test"
        )
        assert key_type == "int"

    def test_detects_str_key_type(self) -> None:
        """Returns 'str' when the first record key is a string."""
        records = [("a", {"_key": "a"}), ("b", {"_key": "b"})]
        key_type, _ = get_key_type_from_records(
            records=iter(records), dataset_name="test"
        )
        assert key_type == "str"

    def test_iterable_not_consumed_by_peek(self) -> None:
        """The returned iterable still yields all original records."""
        records = [(1, {"_key": 1}), (2, {"_key": 2}), (3, {"_key": 3})]
        _, remaining = get_key_type_from_records(
            records=iter(records), dataset_name="test"
        )
        assert len(list(remaining)) == 3

    def test_raises_value_error_for_invalid_key_type(self) -> None:
        """ValueError is raised when the first record key is neither int nor str."""
        records = [(3.14, {"_key": 3.14})]
        with pytest.raises(ValueError):
            get_key_type_from_records(records=iter(records), dataset_name="test")

    def test_raises_on_empty_records(self) -> None:
        """StopIteration is raised when the records iterable is empty."""
        with pytest.raises(StopIteration):
            get_key_type_from_records(records=iter([]), dataset_name="test")


class TestWriteDbMetadata:
    """Tests for write_db_metadata."""

    def test_metadata_is_persisted(
        self,
        rw_connection: sqlite3.Connection,
        sample_metadata: SdeMetadata,
    ) -> None:
        """write_db_metadata stores SDE metadata retrievable via query_sde_metadata."""
        write_db_metadata(
            rw_connection,
            sde_metadata=sample_metadata,
            serialization_format=SerializationFormat.JSON,
        )
        result = query_sde_metadata(rw_connection)
        assert result is not None
        assert result.buildNumber == sample_metadata.buildNumber

    def test_serialization_format_is_persisted(
        self,
        rw_connection: sqlite3.Connection,
        sample_metadata: SdeMetadata,
    ) -> None:
        """write_db_metadata stores the serialization format in DatabaseSettings."""
        write_db_metadata(
            rw_connection,
            sde_metadata=sample_metadata,
            serialization_format=SerializationFormat.YAML,
        )
        row = rw_connection.execute(
            "SELECT serialization_format FROM DatabaseSettings"
        ).fetchone()
        assert row is not None
        assert row[0] == "yaml"


class TestWriteSdeRecordsToDb:
    """Tests for write_sde_records_to_db."""

    def test_writes_int_keyed_records_json(
        self,
        rw_connection: sqlite3.Connection,
        sample_int_records: list[tuple[int, dict]],
    ) -> None:
        """Integer-keyed records are stored and counted correctly with JSON format."""
        count = write_sde_records_to_db(
            rw_connection,
            records=iter(sample_int_records),
            key_type="int",
            dataset_name="agents",
            serialization_format=SerializationFormat.JSON,
        )
        assert count == 3

    def test_writes_str_keyed_records_json(
        self,
        rw_connection: sqlite3.Connection,
        sample_str_records: list[tuple[str, dict]],
    ) -> None:
        """String-keyed records are stored and counted correctly with JSON format."""
        count = write_sde_records_to_db(
            rw_connection,
            records=iter(sample_str_records),
            key_type="str",
            dataset_name="sde_info",
            serialization_format=SerializationFormat.JSON,
        )
        assert count == 2

    def test_writes_int_keyed_records_yaml(
        self,
        rw_connection: sqlite3.Connection,
        sample_int_records: list[tuple[int, dict]],
    ) -> None:
        """Integer-keyed records are stored correctly with YAML format."""
        count = write_sde_records_to_db(
            rw_connection,
            records=iter(sample_int_records),
            key_type="int",
            dataset_name="agents_yaml",
            serialization_format=SerializationFormat.YAML,
        )
        assert count == 3

    def test_writes_int_keyed_records_pickle(
        self,
        rw_connection: sqlite3.Connection,
        sample_int_records: list[tuple[int, dict]],
    ) -> None:
        """Integer-keyed records are stored correctly with Pickle format."""
        count = write_sde_records_to_db(
            rw_connection,
            records=iter(sample_int_records),
            key_type="int",
            dataset_name="agents_pickle",
            serialization_format=SerializationFormat.PICKLE,
        )
        assert count == 3

    def test_key_type_metadata_is_recorded(
        self,
        rw_connection: sqlite3.Connection,
        sample_int_records: list[tuple[int, dict]],
    ) -> None:
        """write_sde_records_to_db records the key type in DatasetKeyType."""
        write_sde_records_to_db(
            rw_connection,
            records=iter(sample_int_records),
            key_type="int",
            dataset_name="cats",
            serialization_format=SerializationFormat.JSON,
        )
        key_types = query_key_types(rw_connection)
        assert key_types.get("cats") == "int"

    def test_raises_value_error_for_unknown_serialization_format(
        self, rw_connection: sqlite3.Connection
    ) -> None:
        """ValueError is raised for an unsupported serialization format."""
        records = [(1, {"_key": 1})]
        with pytest.raises((ValueError, Exception)):
            write_sde_records_to_db(
                rw_connection,
                records=iter(records),
                key_type="int",
                dataset_name="bad",
                serialization_format="unsupported",  # type: ignore[arg-type]
            )
