import sqlite3
from collections.abc import Iterable
from typing import Any

from eve_static_data.db import models_2 as db_models
from eve_static_data.db.helpers import (
    query_int_records,
    query_key_types,
    query_sde_metadata,
    query_str_records,
)
from eve_static_data.helpers.sde_metadata import SdeMetadata


class DatasetDbQuery:
    """A class to query datasets from the database."""

    def __init__(self, connection: sqlite3.Connection):
        """Initialize the DatasetDbQuery with a database connection."""
        self.connection = connection
        self._dataset_key_types: dict[str, str] | None = None
        self._serialization_format: db_models.SerializationFormat | None = None

    @property
    def dataset_key_types(self) -> dict[str, str]:
        """Get the key types for all datasets from the database."""
        if self._dataset_key_types is None:
            self._dataset_key_types = query_key_types(connection=self.connection)
        return self._dataset_key_types

    @property
    def serialization_format(self) -> db_models.SerializationFormat:
        """Get the serialization format used for storing records in the database."""
        if self._serialization_format is None:
            cursor = self.connection.execute(
                "SELECT serialization_format FROM DatabaseSettings WHERE row_id = 1"
            )
            row = cursor.fetchone()
            if row is not None:
                self._serialization_format = db_models.SerializationFormat(
                    row["serialization_format"]
                )
        if self._serialization_format is None:
            raise ValueError(
                "Serialization format not found in DatabaseSettings table. "
                "Ensure that the database has been initialized with a serialization format."
            )
        return self._serialization_format

    @property
    def sde_metadata(self) -> SdeMetadata | None:
        """Get the SDE metadata from the database."""
        return query_sde_metadata(conn=self.connection)

    def get_int_records(
        self, dataset_name: str, record_keys: set[int] | None = None
    ) -> Iterable[tuple[int, dict[str | int, Any]]]:
        """Get records for a dataset with integer keys from the database.

        Args:
            dataset_name (str): The name of the dataset to query.
            record_keys (set[int] | None): An optional set of integer keys to filter the
                records. If None, all records for the dataset will be returned.

        Yields:
            tuple[int, dict[str | int, Any]]: A tuple containing the record key and the
                deserialized record as a dictionary.
        """
        if dataset_name not in self.dataset_key_types:
            raise ValueError(
                f"Dataset '{dataset_name}' not found in the database. "
                "Ensure that the dataset has been loaded into the database."
            )
        if self.dataset_key_types[dataset_name] != "int":
            raise ValueError(
                f"Dataset '{dataset_name}' does not have integer keys. "
                "Use get_str_records for datasets with string keys."
            )
        for record in query_int_records(
            connection=self.connection,
            dataset_name=dataset_name,
            serialization_format=self.serialization_format,
            record_keys=record_keys,
        ):
            yield record.record_key, record.deserialize_record()

    def get_str_records(
        self, dataset_name: str, record_keys: set[str] | None = None
    ) -> Iterable[tuple[str, dict[str | int, Any]]]:
        """Get records for a dataset with string keys from the database.

        Args:
            dataset_name (str): The name of the dataset to query.
            record_keys (set[str] | None): An optional set of string keys to filter the
                records. If None, all records for the dataset will be returned.

        Yields:
            tuple[str, dict[str | int, Any]]: A tuple containing the record key and the
                deserialized record as a dictionary.
        """
        if dataset_name not in self.dataset_key_types:
            raise ValueError(
                f"Dataset '{dataset_name}' not found in the database. "
                "Ensure that the dataset has been loaded into the database."
            )
        if self.dataset_key_types[dataset_name] != "str":
            raise ValueError(
                f"Dataset '{dataset_name}' does not have string keys. "
                "Use get_int_records for datasets with integer keys."
            )
        for record in query_str_records(
            connection=self.connection,
            dataset_name=dataset_name,
            serialization_format=self.serialization_format,
            record_keys=record_keys,
        ):
            yield record.record_key, record.deserialize_record()
