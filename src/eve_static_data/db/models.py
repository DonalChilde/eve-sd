# """Models for the primary database.

# Because of the different way that the same datasets are structured in the YAML and JSONL
# source formats, the expectations are different when going from DatasetRecordInt/Str to
# the original record dict. For YAML source datasets, the key in the record dict is not
# expected to be present, because it is already stored in the record_key field of the
# DatasetRecordInt/Str. The YAML datasets load as dicts, with the record key as the
# dictionary key. For JSONL source datasets, the key in the record dict is expected to be
# present as a top-level key named '_key', because JSONL source datasets are loaded as one
# dict per line. This means the record key must be inside the loaded dict.

# When reconstituting a record, if the source was yaml then the key must come from the
# record_key field of the DatasetRecordInt/Str, and if the source was jsonl then the key
# may come from the '_key' field in the deserialized record_json, or it may come from the
# record_key field. It must be the same value in both places.
# """

# from dataclasses import dataclass
# from typing import Any, Self

# from pydantic_core import from_json, to_json


# @dataclass(slots=True, kw_only=True)
# class DatasetDbRecordInt:
#     record_key: int
#     dataset_name: str
#     record_json: bytes

#     def deserialize_record(self) -> dict[int, Any]:
#         """Deserialize the record JSON into a dictionary."""
#         return from_json(self.record_json)

#     @staticmethod
#     def serialize_record(record: Any) -> bytes:
#         """Serialize the given record dictionary to JSON bytes."""
#         return to_json(record)

#     @classmethod
#     def from_jsonl_record(cls, dataset_name: str, record: dict[str, Any]) -> Self:
#         """Create a DatasetDbRecordInt instance from a record in JSONL format.

#         The record is expected to be a dictionary with a top-level key that is `_key`
#         with a value that is an int.

#         Example:
#             class JsonlRecordBase(TypedDict):
#                 _key: int
#                 ... # other fields
#         """
#         if not isinstance(record, dict):  # pyright: ignore[reportUnnecessaryIsInstance]
#             raise ValueError("record must be a dictionary.")
#         record_key_int = record.get("_key")
#         if not isinstance(record_key_int, int):
#             raise ValueError(
#                 "record must contain a top-level key '_key' with an integer value."
#             )

#         return cls(
#             record_key=record_key_int,
#             dataset_name=dataset_name,
#             record_json=cls.serialize_record(record),
#         )

#     @classmethod
#     def from_yaml_record(cls, dataset_name: str, record_key: int, record: Any) -> Self:
#         """Create a DatasetDbRecordInt instance from a record in YAML format.

#         The entire record is serialized to JSON and stored as bytes in the record_json field.
#         """
#         if not isinstance(record_key, int):  # pyright: ignore[reportUnnecessaryIsInstance]
#             raise ValueError("The key in record must be an integer.")

#         return cls(
#             record_key=record_key,
#             dataset_name=dataset_name,
#             record_json=cls.serialize_record(record),
#         )


# @dataclass(slots=True, kw_only=True)
# class DatasetDbRecordStr:
#     record_key: str
#     dataset_name: str
#     record_json: bytes

#     def deserialize_record(self) -> dict[str, Any]:
#         """Deserialize the record JSON into a dictionary."""
#         return from_json(self.record_json)

#     @staticmethod
#     def serialize_record(record: Any) -> bytes:
#         """Serialize the given record dictionary to JSON bytes."""
#         return to_json(record)

#     @classmethod
#     def from_jsonl_record(cls, dataset_name: str, record: dict[str, Any]) -> Self:
#         """Create a DatasetDbRecordStr instance from a record in JSONL format.

#         The record is expected to be a dictionary with a top-level key that is `_key`
#         with a value that is a str.

#         Example:
#             class JsonlRecordBase(TypedDict):
#                 _key: str
#                 ... # other fields
#         """
#         if not isinstance(record, dict):  # pyright: ignore[reportUnnecessaryIsInstance]
#             raise ValueError("record must be a dictionary.")
#         record_key_str = record.get("_key")
#         if not isinstance(record_key_str, str):
#             raise ValueError(
#                 "record must contain a top-level key '_key' with a string value."
#             )

#         return cls(
#             record_key=record_key_str,
#             dataset_name=dataset_name,
#             record_json=cls.serialize_record(record),
#         )

#     @classmethod
#     def from_yaml_record(cls, dataset_name: str, record_key: str, record: Any) -> Self:
#         """Create a DatasetDbRecordStr instance from a record in YAML format.

#         The entire record is serialized to JSON and stored as bytes in the record_json field.
#         """
#         if not isinstance(record_key, str):  # pyright: ignore[reportUnnecessaryIsInstance]
#             raise ValueError("The key in record must be a string.")

#         return cls(
#             record_key=record_key,
#             dataset_name=dataset_name,
#             record_json=cls.serialize_record(record),
#         )
