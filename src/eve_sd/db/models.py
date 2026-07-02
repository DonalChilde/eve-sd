"""Database record model classes and serialization helpers.

Records are stored in SQLite as bytes. Concrete model classes combine key type
(``str`` or ``int``) and serialization format (YAML, JSON, or pickle) so load
and save paths can choose the correct conversion behavior. In table storage,
``record_key`` and ``dataset_name`` map to columns used for logical identity,
while ``row_id`` remains the SQLite primary key.

Example:
    record = {"_key": "example_key", "field1": "value1", "field2": 42}
    dataset_record = DatasetRecordStrYaml(
        record_key=record["_key"],
        dataset_name="example_dataset",
        record=DatasetRecordStrYaml.serialize_record(record),
    )
    assert dataset_record.deserialize_record() == record
"""

import pickle
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Protocol, Self

from eve_sd import IntKeyedRecord, Record, StrKeyedRecord
from eve_sd.helpers import json_io, yaml_io


class SerializationFormat(StrEnum):
    """Supported on-disk serialization formats for stored record bytes."""

    YAML = "yaml"
    JSON = "json"
    PICKLE = "pickle"


@dataclass(slots=True, kw_only=True)
class DatasetRecordBase:
    """Base dataclass for one serialized dataset record.

    Attributes:
        record_key: Record identifier value from the source dataset.
        dataset_name: Dataset name this record belongs to.
        record: Serialized record payload as raw bytes.
    """

    record_key: Any
    dataset_name: str
    record: bytes

    @staticmethod
    def serialize_record(record: Record) -> bytes:
        """Serialize a typed record mapping into raw bytes.

        Args:
            record: Record mapping to serialize.

        Returns:
            Byte representation of the input record.
        """
        raise NotImplementedError(
            "This method should be implemented in subclasses to serialize the record."
        )

    def deserialize_record(self) -> Record:
        """Deserialize this instance's raw record bytes into a Python value.

        Returns:
            Deserialized record payload.
        """
        raise NotImplementedError(
            "This method should be implemented in subclasses to deserialize the record bytes."
        )


class SerializerProtocol(Protocol):
    """Protocol for serializer behavior used by concrete record classes."""

    @staticmethod
    def serialize_record(record: Record) -> bytes:
        """Serialize a record to bytes."""
        raise NotImplementedError(
            "This method should be implemented in subclasses to serialize the record."
        )

    def deserialize_record(self) -> Record:
        """Deserialize record bytes into a typed record mapping."""
        raise NotImplementedError(
            "This method should be implemented in subclasses to deserialize the record bytes."
        )


@dataclass(slots=True, kw_only=True)
class DatasetRecordStrBase(DatasetRecordBase):
    """Base model for rows where the ``record_key`` column is text."""

    record_key: str

    @classmethod
    def from_record(cls, dataset_name: str, keyed_record: StrKeyedRecord) -> Self:
        """Create a string-keyed model instance from an in-memory record.

        Args:
            dataset_name: Dataset/table name for storage.
            keyed_record: ``(record_key, record)`` tuple.

        Returns:
            New model instance with serialized ``record`` bytes.
        """
        record_key, record = keyed_record
        return cls(
            record_key=record_key,
            dataset_name=dataset_name,
            record=cls.serialize_record(record),
        )


@dataclass(slots=True, kw_only=True)
class DatasetRecordIntBase(DatasetRecordBase):
    """Base model for rows where the ``record_key`` column is integer."""

    record_key: int

    @classmethod
    def from_record(cls, dataset_name: str, keyed_record: IntKeyedRecord) -> Self:
        """Create an integer-keyed model instance from an in-memory record.

        Args:
            dataset_name: Dataset/table name for storage.
            keyed_record: ``(record_key, record)`` tuple.

        Returns:
            New model instance with serialized ``record`` bytes.
        """
        record_key, record = keyed_record
        return cls(
            record_key=record_key,
            dataset_name=dataset_name,
            record=cls.serialize_record(record),
        )


@dataclass(slots=True, kw_only=True)
class DatasetRecordStrYaml(DatasetRecordStrBase):
    """String-keyed record model using YAML serialization."""

    def deserialize_record(self) -> Record:
        """Deserialize YAML bytes into a record mapping."""
        record = yaml_io.safe_load(self.record)
        return record

    @staticmethod
    def serialize_record(record: Record) -> bytes:
        """Serialize a record mapping to UTF-8 YAML bytes."""
        return yaml_io.safe_dump(record).encode("utf-8")


@dataclass(slots=True, kw_only=True)
class DatasetRecordIntYaml(DatasetRecordIntBase):
    """Integer-keyed record model using YAML serialization."""

    def deserialize_record(self) -> Record:
        """Deserialize YAML bytes into a record mapping."""
        record = yaml_io.safe_load(self.record)
        return record

    @staticmethod
    def serialize_record(record: Record) -> bytes:
        """Serialize a record mapping to UTF-8 YAML bytes."""
        return yaml_io.safe_dump(record).encode("utf-8")


@dataclass(slots=True, kw_only=True)
class DatasetRecordStrJson(DatasetRecordStrBase):
    """String-keyed record model using JSON serialization."""

    def deserialize_record(self) -> Record:
        """Deserialize JSON bytes into a record mapping."""
        record = json_io.json_loads(self.record)
        return record

    @staticmethod
    def serialize_record(record: Record) -> bytes:
        """Serialize a record mapping to UTF-8 JSON bytes."""
        return json_io.json_dumps(record).encode("utf-8")


@dataclass(slots=True, kw_only=True)
class DatasetRecordIntJson(DatasetRecordIntBase):
    """Integer-keyed record model using JSON serialization."""

    def deserialize_record(self) -> Record:
        """Deserialize JSON bytes into a record mapping."""
        record = json_io.json_loads(self.record)
        return record

    @staticmethod
    def serialize_record(record: Record) -> bytes:
        """Serialize a record mapping to UTF-8 JSON bytes."""
        return json_io.json_dumps(record).encode("utf-8")


@dataclass(slots=True, kw_only=True)
class DatasetRecordStrPickle(DatasetRecordStrBase):
    """String-keyed record model using pickle serialization.

    Note:
        Pickle is Python-specific and should only be deserialized from trusted
        sources.
    """

    def deserialize_record(self) -> Record:
        """Deserialize pickle bytes into a record mapping."""
        record = pickle.loads(self.record)
        return record

    @staticmethod
    def serialize_record(record: Record) -> bytes:
        """Serialize a record mapping to pickle bytes."""
        return pickle.dumps(record)


@dataclass(slots=True, kw_only=True)
class DatasetRecordIntPickle(DatasetRecordIntBase):
    """Integer-keyed record model using pickle serialization.

    Note:
        Pickle is Python-specific and should only be deserialized from trusted
        sources.
    """

    def deserialize_record(self) -> Record:
        """Deserialize pickle bytes into a record mapping."""
        record = pickle.loads(self.record)
        return record

    @staticmethod
    def serialize_record(record: Record) -> bytes:
        """Serialize a record mapping to pickle bytes."""
        return pickle.dumps(record)
