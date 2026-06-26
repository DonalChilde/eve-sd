import sqlite3
from collections.abc import Iterable
from typing import Any

from eve_static_data.db.helpers import (
    query_int_records,
    query_key_types,
    query_sde_metadata,
    query_str_records,
)
from eve_static_data.helpers import json_io
from eve_static_data.helpers.sde_metadata import SdeMetadata


class DatasetDbQuery:
    """A class to query datasets from the database."""

    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection
        self._dataset_key_types: dict[str, str] | None = None

    @property
    def dataset_key_types(self) -> dict[str, str]:
        """Get the key types for all datasets from the database."""
        if self._dataset_key_types is None:
            self._dataset_key_types = query_key_types(conn=self.connection)
        return self._dataset_key_types

    @property
    def sde_metadata(self) -> SdeMetadata | None:
        """Get the SDE metadata from the database."""
        return query_sde_metadata(conn=self.connection)

    def get_int_records(
        self, dataset_name: str, record_keys: set[int] | None = None
    ) -> Iterable[tuple[int, dict[str, Any]]]:
        """Get records for a dataset with integer keys from the database.

        Args:
            dataset_name (str): The name of the dataset to query.
            record_keys (set[int] | None): An optional set of integer keys to filter the
                records. If None, all records for the dataset will be returned.

        Yields:
            tuple[int, dict[str, Any]]: A tuple containing the record key and the
                deserialized record as a dictionary.
        """
        for record in query_int_records(
            conn=self.connection, dataset_name=dataset_name, record_keys=record_keys
        ):
            yield record.record_key, json_io.json_loads(record.record_json)

    def get_str_records(
        self, dataset_name: str, record_keys: set[str] | None = None
    ) -> Iterable[tuple[str, dict[str, Any]]]:
        """Get records for a dataset with string keys from the database.

        Args:
            dataset_name (str): The name of the dataset to query.
            record_keys (set[str] | None): An optional set of string keys to filter the
                records. If None, all records for the dataset will be returned.

        Yields:
            tuple[str, dict[str, Any]]: A tuple containing the record key and the
                deserialized record as a dictionary.
        """
        for record in query_str_records(
            conn=self.connection, dataset_name=dataset_name, record_keys=record_keys
        ):
            yield record.record_key, json_io.json_loads(record.record_json)
