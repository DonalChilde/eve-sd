# """Loader for loading SDE records from yaml-format sources.

# This is the primary entry point for loading SDE records from yaml-format sources.
# """

# import logging
# import sqlite3
# from collections.abc import Iterable
# from pathlib import Path
# from typing import Any

# from pydantic import ValidationError

# from eve_static_data.db.query import DatasetDbQuery
# from eve_static_data.helpers.load_raw_datasets import load_dataset_from_file
# from eve_static_data.helpers.sde_metadata import (
#     SdeMetadata,
#     load_sde_metadata,
# )
# from eve_static_data.models.common import DatasetRecordBase
# from eve_static_data.models.dataset_filenames import SdeDatasets
# from eve_static_data.models.yaml_format.yaml_record_root import (
#     get_root_model_for_record,
# )
# from eve_static_data.record_loader.protocols import LoaderProtocol

# logger = logging.getLogger(__name__)


# def deserialize_yaml_record[T: DatasetRecordBase](
#     record_model: type[T], *, record_key: int | str, record_dict: dict[str, Any]
# ) -> T | ValidationError:
#     """Deserialize a raw record dictionary into a yaml-format record model instance.

#     Adds the record_key to the record_dict before deserializing into the record_model.

#     Returning a ValidationError indicates that the record_dict is invalid for the record_model.

#     Args:
#         record_model (type[T]): A subclass of DatasetRecordBase that specifies
#             the dataset to load.
#         record_key (int | str): The key of the record being deserialized.
#         record_dict (dict[str, Any]): The raw record dictionary to deserialize.

#     Returns:
#         T | ValidationError: The deserialized record model instance, or a
#             ValidationError if the record_dict is invalid for the record_model.
#     """
#     root_model = get_root_model_for_record(record_model)
#     modified_record_dict: dict[str, Any] = {**record_dict, "record_key": record_key}
#     try:
#         record = root_model.model_validate(modified_record_dict).root
#         return record
#     except ValidationError as e:
#         return e


# class YamlFileLoader(LoaderProtocol):
#     def __init__(self, sde_path: Path):
#         """Initialize the loader with the path to the SDE directory."""
#         self._sde_path = sde_path
#         self._sde_metadata: SdeMetadata | None = None

#     def sde_metadata(self) -> SdeMetadata:
#         """Get the SDE metadata, loading it from the SDE path if necessary."""
#         if self._sde_metadata is None:
#             self._sde_metadata = load_sde_metadata(self._sde_path)
#         return self._sde_metadata

#     def load_records[T: DatasetRecordBase](
#         self,
#         record_model: type[T],
#         *,
#         record_keys: set[int | str] | None = None,
#     ) -> Iterable[tuple[int | str, T]]:
#         """Load records from a dataset.

#         The dataset is determined by the record_model's dataset attribute. If record_keys
#         is provided, only records with those keys will be loaded.

#         Record instances are created by deserializing the raw records using Pydantic,
#         which provides validation of the raw records. If a raw record fails validation,
#         a ValidationError will be raised.

#         Args:
#             record_model (type[T]): A subclass of DatasetRecordBase that specifies
#                 the dataset to load.
#             record_keys (set[int | str] | None): Optional set of keys to filter the
#                 records. If None, all records will be loaded.

#         Returns:
#             Iterable[tuple[int | str, T]]: An iterable of tuples, each containing a
#                 record key and the corresponding record instance.

#         Raises:
#             ValidationError: If a raw record fails validation when deserializing into
#                 the record_model.
#         """
#         for record_key, record_dict in self.load_raw_records(
#             record_model.dataset, record_keys=record_keys
#         ):
#             record = deserialize_yaml_record(
#                 record_model, record_key=record_key, record_dict=record_dict
#             )
#             if isinstance(record, ValidationError):
#                 raise record
#             yield record_key, record

#     def load_raw_records(
#         self, dataset: SdeDatasets, *, record_keys: set[int | str] | None = None
#     ) -> Iterable[tuple[int | str, dict[str, Any]]]:
#         """Load raw records from a dataset file.

#         The dataset is determined by the dataset argument. If record_keys is provided,
#         only records with those keys will be loaded.

#         Raw records are returned as dictionaries without any validation. If a record is
#         missing a required field or has an invalid type, it will be returned as-is.

#         Args:
#             dataset (SdeDatasets): The dataset to load.
#             record_keys (set[int | str] | None): Optional set of keys to filter the
#                 records. If None, all records will be loaded.

#         Returns:
#             Iterable[tuple[int | str, dict[str, Any]]]: An iterable of tuples, each
#                 containing a record key and the corresponding raw record dictionary.

#         Raises:
#             FileNotFoundError: If the dataset file does not exist.
#             ValueError: If the dataset file is not a valid YAML file.
#         """
#         dataset_dict, source_format = load_dataset_from_file(
#             dataset, sde_path=self._sde_path
#         )
#         if source_format != "yaml-model":
#             raise ValueError(
#                 f"Expected a YAML mapping (dict) in file '{dataset.value}', but got {source_format}."
#             )
#         # log request for keys that are not present in the dataset
#         if record_keys is not None:
#             missing_keys = record_keys - dataset_dict.keys()
#             if missing_keys:
#                 logger.warning(
#                     f"Requested record keys {missing_keys} not found in dataset '{dataset.value}'."
#                 )
#         for key, record in dataset_dict.items():
#             if record_keys is None or key in record_keys:
#                 yield key, record


# class YamlDBLoader(LoaderProtocol):
#     def __init__(self, connection: sqlite3.Connection):
#         """Initialize the loader with a SQLite database connection."""
#         self._connection = connection
#         self._dataset_query = DatasetDbQuery(connection)

#     @property
#     def dataset_key_types(self) -> dict[str, str]:
#         """Get the dataset key types from the database.

#         Returns:
#             dict[str, str]: A dictionary mapping dataset names to their key types.
#         """
#         return self._dataset_query.dataset_key_types

#     def sde_metadata(self) -> SdeMetadata:
#         """Get the SDE metadata, loading it from the SDE path if necessary."""
#         sde_metadata = self._dataset_query.sde_metadata
#         if sde_metadata is None:
#             raise ValueError("SDE metadata not found in the database.")
#         return sde_metadata

#     def load_records[T: DatasetRecordBase](
#         self,
#         record_model: type[T],
#         *,
#         record_keys: set[int | str] | None = None,
#     ) -> Iterable[tuple[int | str, T]]:
#         """Load records from a dataset.

#         The dataset is determined by the record_model's dataset attribute. If record_keys
#         is provided, only records with those keys will be loaded.

#         Record instances are created by deserializing the raw records using Pydantic,
#         which provides validation of the raw records. If a raw record fails validation,
#         a ValidationError will be raised.

#         Args:
#             record_model (type[T]): A subclass of DatasetRecordBase that specifies
#                 the dataset to load.
#             record_keys (set[int | str] | None): Optional set of keys to filter the
#                 records. If None, all records will be loaded.

#         Returns:
#             Iterable[tuple[int | str, T]]: An iterable of tuples, each containing a
#                 record key and the corresponding record instance.

#         Raises:
#             ValidationError: If a raw record fails validation when deserializing into
#                 the record_model.
#         """
#         for record_key, record_dict in self.load_raw_records(
#             record_model.dataset, record_keys=record_keys
#         ):
#             record = deserialize_yaml_record(
#                 record_model, record_key=record_key, record_dict=record_dict
#             )
#             if isinstance(record, ValidationError):
#                 raise record
#             yield record_key, record

#     def load_raw_records(
#         self, dataset: SdeDatasets, *, record_keys: set[int | str] | None = None
#     ) -> Iterable[tuple[int | str, dict[str, Any]]]:
#         """Load raw records from a dataset file.

#         The dataset is determined by the dataset argument. If record_keys is provided,
#         only records with those keys will be loaded.

#         Raw records are returned as dictionaries without any validation. If a record is
#         missing a required field or has an invalid type, it will be returned as-is.

#         Args:
#             dataset (SdeDatasets): The dataset to load.
#             record_keys (set[int | str] | None): Optional set of keys to filter the
#                 records. If None, all records will be loaded.

#         Returns:
#             Iterable[tuple[int | str, dict[str, Any]]]: An iterable of tuples, each
#                 containing a record key and the corresponding raw record dictionary.

#         Raises:
#             FileNotFoundError: If the dataset file does not exist.
#             ValueError: If the dataset file is not a valid YAML file.
#         """
#         key_type = self._dataset_query.dataset_key_types.get(dataset.value)
#         if key_type is None:
#             raise ValueError(
#                 f"Dataset '{dataset.value}' not found in the database. "
#                 "Ensure that the dataset has been loaded into the database."
#             )
#         match key_type:
#             case "int":
#                 if record_keys is not None and not all(
#                     isinstance(k, int) for k in record_keys
#                 ):
#                     raise ValueError(
#                         f"Expected integer keys for dataset '{dataset.value}', but got {record_keys}."
#                     )

#                 yield from self._dataset_query.get_int_records(
#                     dataset_name=dataset.value,
#                     record_keys=record_keys,  # type: ignore
#                 )
#             case "str":
#                 if record_keys is not None and not all(
#                     isinstance(k, str) for k in record_keys
#                 ):
#                     raise ValueError(
#                         f"Expected string keys for dataset '{dataset.value}', but got {record_keys}."
#                     )
#                 yield from self._dataset_query.get_str_records(
#                     dataset_name=dataset.value,
#                     record_keys=record_keys,  # type: ignore
#                 )
#             case _:
#                 raise ValueError(
#                     f"Unexpected key type '{key_type}' for dataset '{dataset.value}'."
#                 )
