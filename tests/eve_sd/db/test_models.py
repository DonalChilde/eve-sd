"""Tests for eve_sd.db.models serialization."""

import pytest

from eve_sd.db.models import (
    DatasetRecordIntJson,
    DatasetRecordIntPickle,
    DatasetRecordIntYaml,
    DatasetRecordStrJson,
    DatasetRecordStrPickle,
    DatasetRecordStrYaml,
)

SAMPLE_INT_RECORD: dict = {"_key": 42, "name": "Stargate", "active": True}
SAMPLE_STR_RECORD: dict = {"_key": "alpha", "name": "Alpha Corp", "count": 7}


class TestDatasetRecordStrYaml:
    """Tests for DatasetRecordStrYaml serialization."""

    def test_serialize_produces_bytes(self) -> None:
        """serialize_record returns bytes."""
        result = DatasetRecordStrYaml.serialize_record(SAMPLE_STR_RECORD)
        assert isinstance(result, bytes)

    def test_round_trip_via_from_record(self) -> None:
        """from_record → deserialize_record preserves the original record."""
        instance = DatasetRecordStrYaml.from_record(
            "test_dataset", ("alpha", SAMPLE_STR_RECORD)
        )
        assert instance.deserialize_record() == SAMPLE_STR_RECORD

    def test_from_record_sets_key_and_dataset(self) -> None:
        """from_record sets record_key and dataset_name correctly."""
        instance = DatasetRecordStrYaml.from_record(
            "my_dataset", ("alpha", SAMPLE_STR_RECORD)
        )
        assert instance.record_key == "alpha"
        assert instance.dataset_name == "my_dataset"


class TestDatasetRecordIntYaml:
    """Tests for DatasetRecordIntYaml serialization."""

    def test_round_trip_via_from_record(self) -> None:
        """from_record → deserialize_record preserves the original record."""
        instance = DatasetRecordIntYaml.from_record(
            "test_dataset", (42, SAMPLE_INT_RECORD)
        )
        assert instance.deserialize_record() == SAMPLE_INT_RECORD

    def test_from_record_sets_int_key(self) -> None:
        """from_record sets record_key as an integer."""
        instance = DatasetRecordIntYaml.from_record(
            "ds", (42, SAMPLE_INT_RECORD)
        )
        assert instance.record_key == 42
        assert isinstance(instance.record_key, int)


class TestDatasetRecordStrJson:
    """Tests for DatasetRecordStrJson serialization."""

    def test_serialize_produces_bytes(self) -> None:
        """serialize_record returns bytes."""
        result = DatasetRecordStrJson.serialize_record(SAMPLE_STR_RECORD)
        assert isinstance(result, bytes)

    def test_round_trip_via_from_record(self) -> None:
        """from_record → deserialize_record preserves the original record."""
        instance = DatasetRecordStrJson.from_record(
            "test_dataset", ("alpha", SAMPLE_STR_RECORD)
        )
        assert instance.deserialize_record() == SAMPLE_STR_RECORD


class TestDatasetRecordIntJson:
    """Tests for DatasetRecordIntJson serialization."""

    def test_round_trip_via_from_record(self) -> None:
        """from_record → deserialize_record preserves the original record."""
        instance = DatasetRecordIntJson.from_record(
            "test_dataset", (42, SAMPLE_INT_RECORD)
        )
        assert instance.deserialize_record() == SAMPLE_INT_RECORD


class TestDatasetRecordStrPickle:
    """Tests for DatasetRecordStrPickle serialization."""

    def test_serialize_produces_bytes(self) -> None:
        """serialize_record returns bytes."""
        result = DatasetRecordStrPickle.serialize_record(SAMPLE_STR_RECORD)
        assert isinstance(result, bytes)

    def test_round_trip_via_from_record(self) -> None:
        """from_record → deserialize_record preserves the original record."""
        instance = DatasetRecordStrPickle.from_record(
            "test_dataset", ("alpha", SAMPLE_STR_RECORD)
        )
        assert instance.deserialize_record() == SAMPLE_STR_RECORD


class TestDatasetRecordIntPickle:
    """Tests for DatasetRecordIntPickle serialization."""

    def test_round_trip_via_from_record(self) -> None:
        """from_record → deserialize_record preserves the original record."""
        instance = DatasetRecordIntPickle.from_record(
            "test_dataset", (42, SAMPLE_INT_RECORD)
        )
        assert instance.deserialize_record() == SAMPLE_INT_RECORD


class TestSerializationFormatsDiffer:
    """Verify that YAML, JSON, and Pickle produce distinct byte payloads."""

    def test_str_formats_produce_different_bytes(self) -> None:
        """The three string-keyed serializers emit different byte sequences."""
        yaml_bytes = DatasetRecordStrYaml.serialize_record(SAMPLE_STR_RECORD)
        json_bytes = DatasetRecordStrJson.serialize_record(SAMPLE_STR_RECORD)
        pickle_bytes = DatasetRecordStrPickle.serialize_record(SAMPLE_STR_RECORD)
        assert yaml_bytes != json_bytes
        assert json_bytes != pickle_bytes

    def test_int_formats_produce_different_bytes(self) -> None:
        """The three integer-keyed serializers emit different byte sequences."""
        yaml_bytes = DatasetRecordIntYaml.serialize_record(SAMPLE_INT_RECORD)
        json_bytes = DatasetRecordIntJson.serialize_record(SAMPLE_INT_RECORD)
        pickle_bytes = DatasetRecordIntPickle.serialize_record(SAMPLE_INT_RECORD)
        assert yaml_bytes != json_bytes
        assert json_bytes != pickle_bytes
