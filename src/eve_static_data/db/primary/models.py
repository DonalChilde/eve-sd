from dataclasses import dataclass
from typing import Any, Self

from pydantic_core import from_json, to_json


@dataclass(slots=True, kw_only=True)
class DatasetRecordInt:
    record_key: int
    dataset_name: str
    record_json: bytes

    def from_json(self) -> dict[int, Any]:
        """Deserialize the record JSON into a dictionary."""
        return from_json(self.record_json)

    @classmethod
    def to_json(cls, dataset_name: str, record: dict[int, Any]) -> Self:
        """Create a DatasetRecordInt instance from the given data.

        The record is a dictionary with a single integer key, which is used as the
        record_key for the DatasetRecordInt instance. The entire record dictionary
        is serialized to JSON and stored as bytes in the record_json field.
        """
        if len(record) != 1:
            raise ValueError("record must contain exactly one key-value pair.")
        record_key = next(iter(record.keys()))
        if not isinstance(record_key, int):  # pyright: ignore[reportUnnecessaryIsInstance]
            raise ValueError("The key in record must be an integer.")
        return cls(
            record_key=record_key,
            dataset_name=dataset_name,
            record_json=to_json(record),
        )


@dataclass(slots=True, kw_only=True)
class DatasetRecordStr:
    record_key: str
    dataset_name: str
    record_json: bytes

    def from_json(self) -> dict[str, Any]:
        """Deserialize the record JSON into a dictionary."""
        return from_json(self.record_json)

    @classmethod
    def to_json(cls, dataset_name: str, record: dict[str, Any]) -> Self:
        """Create a DatasetRecordStr instance from the given data.

        The record is a dictionary with a single string key, which is used as the
        record_key for the DatasetRecordStr instance. The entire record dictionary
        is serialized to JSON and stored as bytes in the record_json field.
        """
        if len(record) != 1:
            raise ValueError("record must contain exactly one key-value pair.")
        record_key = next(iter(record.keys()))
        if not isinstance(record_key, str):  # pyright: ignore[reportUnnecessaryIsInstance]
            raise ValueError("The key in record must be a string.")
        return cls(
            record_key=record_key,
            dataset_name=dataset_name,
            record_json=to_json(record),
        )
