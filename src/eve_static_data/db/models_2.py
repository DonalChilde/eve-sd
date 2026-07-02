"""Models for serializing and deserializing dataset records to and from the database.

records are stored in the database as bytes, and the serialization format is determined
by the DatasetRecord subclass used, and the serializer mixin. The following subclasses are provided:
- DatasetRecordStr: For records with string keys.
- DatasetRecordInt: For records with integer keys.

with the following serializer mixins:
- YamlRecord: For serializing and deserializing records in YAML format.
- JsonRecord: For serializing and deserializing records in JSON format.
- PickleRecord: For serializing and deserializing records in Pickle format.

Example:
    # Create a DatasetRecordStrYaml instance that serializes a record to YAML bytes and
    # deserializes it back to a dictionary.
    record = {"_key": "example_key", "field1": "value1", "field2": 42}
    dataset_record = DatasetRecordStrYaml(
        record_key=record["_key"],
        dataset_name="example_dataset",
        record=DatasetRecordStrYaml.serialize_record(record),
    )
    deserialized_record = dataset_record.deserialize_record()
    assert deserialized_record == record
"""

import pickle
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Protocol, Self

from eve_static_data import IntKeyedRecord, Record, StrKeyedRecord
from eve_static_data.helpers import json_io, yaml_io


class SerializationFormat(StrEnum):
    YAML = "yaml"
    JSON = "json"
    PICKLE = "pickle"


@dataclass(slots=True, kw_only=True)
class DatasetRecordBase:
    record_key: Any
    dataset_name: str
    record: bytes

    @staticmethod
    def serialize_record(record: Record) -> bytes:
        """Serialize the given record to bytes."""
        raise NotImplementedError(
            "This method should be implemented in subclasses to serialize the record."
        )

    def deserialize_record(self) -> Any:
        """Deserialize the record bytes."""
        raise NotImplementedError(
            "This method should be implemented in subclasses to deserialize the record bytes."
        )


class SerializerProtocol(Protocol):
    @staticmethod
    def serialize_record(record: Record) -> bytes:
        """Serialize the given record to bytes."""
        raise NotImplementedError(
            "This method should be implemented in subclasses to serialize the record."
        )

    def deserialize_record(self) -> Record:
        """Deserialize the record bytes."""
        raise NotImplementedError(
            "This method should be implemented in subclasses to deserialize the record bytes."
        )


@dataclass(slots=True, kw_only=True)
class DatasetRecordStrBase(DatasetRecordBase):
    record_key: str

    @classmethod
    def from_record(cls, dataset_name: str, keyed_record: StrKeyedRecord) -> Self:
        """Create a DatasetRecordStrBase instance from a record dictionary."""
        record_key, record = keyed_record
        return cls(
            record_key=record_key,
            dataset_name=dataset_name,
            record=cls.serialize_record(record),
        )


@dataclass(slots=True, kw_only=True)
class DatasetRecordIntBase(DatasetRecordBase):
    record_key: int

    @classmethod
    def from_record(cls, dataset_name: str, keyed_record: IntKeyedRecord) -> Self:
        """Create a DatasetRecordIntBase instance from a record dictionary."""
        record_key, record = keyed_record
        return cls(
            record_key=record_key,
            dataset_name=dataset_name,
            record=cls.serialize_record(record),
        )


@dataclass(slots=True, kw_only=True)
class DatasetRecordStrYaml(DatasetRecordStrBase):
    """A dataset record with a string key and YAML serialization."""

    def deserialize_record(self) -> Record:
        """Deserialize the record bytes."""
        record = yaml_io.safe_load(self.record)
        return record

    @staticmethod
    def serialize_record(record: Record) -> bytes:
        """Serialize the given record to YAML bytes."""
        return yaml_io.safe_dump(record).encode("utf-8")


@dataclass(slots=True, kw_only=True)
class DatasetRecordIntYaml(DatasetRecordIntBase):
    """A dataset record with an integer key and YAML serialization."""

    def deserialize_record(self) -> Record:
        """Deserialize the record bytes."""
        record = yaml_io.safe_load(self.record)
        return record

    @staticmethod
    def serialize_record(record: Record) -> bytes:
        """Serialize the given record to YAML bytes."""
        return yaml_io.safe_dump(record).encode("utf-8")


@dataclass(slots=True, kw_only=True)
class DatasetRecordStrJson(DatasetRecordStrBase):
    """A dataset record with a string key and JSON serialization."""

    def deserialize_record(self) -> Record:
        """Deserialize the record bytes."""
        record = json_io.json_loads(self.record)
        return record

    @staticmethod
    def serialize_record(record: Record) -> bytes:
        """Serialize the given record to JSON bytes."""
        return json_io.json_dumps(record).encode("utf-8")


@dataclass(slots=True, kw_only=True)
class DatasetRecordIntJson(DatasetRecordIntBase):
    """A dataset record with an integer key and JSON serialization."""

    def deserialize_record(self) -> Record:
        """Deserialize the record bytes."""
        record = json_io.json_loads(self.record)
        return record

    @staticmethod
    def serialize_record(record: Record) -> bytes:
        """Serialize the given record to JSON bytes."""
        return json_io.json_dumps(record).encode("utf-8")


@dataclass(slots=True, kw_only=True)
class DatasetRecordStrPickle(DatasetRecordStrBase):
    """A dataset record with a string key and Pickle serialization."""

    def deserialize_record(self) -> Record:
        """Deserialize the record bytes."""
        record = pickle.loads(self.record)
        return record

    @staticmethod
    def serialize_record(record: Record) -> bytes:
        """Serialize the given record to Pickle bytes."""
        return pickle.dumps(record)


@dataclass(slots=True, kw_only=True)
class DatasetRecordIntPickle(DatasetRecordIntBase):
    """A dataset record with an integer key and Pickle serialization."""

    def deserialize_record(self) -> Record:
        """Deserialize the record bytes."""
        record = pickle.loads(self.record)
        return record

    @staticmethod
    def serialize_record(record: Record) -> bytes:
        """Serialize the given record to Pickle bytes."""
        return pickle.dumps(record)
