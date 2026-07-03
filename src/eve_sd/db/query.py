"""Public query API for reading SDE datasets from SQLite.

This module provides a thin, typed wrapper around lower-level SQL helper
functions and returns deserialized record payloads.
"""

import sqlite3
from collections.abc import Iterable

from eve_sd import Dataset, IntKeyedRecord, KeyedRecord, StrKeyedRecord
from eve_sd.db import models as db_models
from eve_sd.db.helpers import (
    query_dataset_record_count,
    query_int_records,
    query_int_records_page,
    query_key_types,
    query_sde_metadata,
    query_str_records,
    query_str_records_page,
)
from eve_sd.helpers.sde_metadata import SdeMetadata


class DatasetDbQuery:
    """High-level read/query interface for an SDE SQLite database.

    The class caches dataset key types, serialization format, and dataset record
    counts after first access.
    """

    def __init__(self, connection: sqlite3.Connection):
        """Initialize a query wrapper for an existing SQLite connection.

        Args:
            connection: Open SQLite connection for SDE tables.
        """
        self.connection = connection
        self._dataset_key_types: dict[str, str] | None = None
        self._serialization_format: db_models.SerializationFormat | None = None
        self._dataset_record_counts: dict[str, int] | None = None

    @property
    def dataset_key_types(self) -> dict[str, str]:
        """Return key-type metadata for all datasets.

        Returns:
            Mapping of dataset name to key type (``"int"`` or ``"str"``).
        """
        if self._dataset_key_types is None:
            self._dataset_key_types = query_key_types(connection=self.connection)
        return self._dataset_key_types

    @property
    def serialization_format(self) -> db_models.SerializationFormat:
        """Return the database serialization format for stored record bytes.

        Returns:
            Serialization format declared in ``DatabaseSettings``.

        Raises:
            ValueError: If no serialization format is configured.
        """
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
    def sde_metadata(self) -> SdeMetadata:
        """Return the latest stored SDE metadata row.

        Returns:
            SdeMetadata instance with build number, release date, and variant.

        Raises:
            ValueError: If the SDE metadata is not found in the database.
        """
        sde_metadata = query_sde_metadata(connection=self.connection)
        if sde_metadata is None:
            raise ValueError(
                "SDE metadata not found in the database. Ensure that the database has been initialized with SDE metadata."
            )
        return sde_metadata

    @property
    def dataset_record_counts(self) -> dict[str, int]:
        """Return record counts for all datasets.

        Returns:
            Mapping of dataset name to record count.
        """
        if self._dataset_record_counts is None:
            self._dataset_record_counts = {
                dataset_name: self._get_dataset_record_count(dataset_name)
                for dataset_name in self.dataset_key_types
            }
        return self._dataset_record_counts

    def _get_dataset_record_count(self, dataset_name: str) -> int:
        """Return record count for a single dataset.

        Args:
            dataset_name: Dataset name to count.

        Returns:
            Number of stored records for the dataset.

        Raises:
            ValueError: If the dataset is not present in key-type metadata.
        """
        if dataset_name not in self.dataset_key_types:
            raise ValueError(
                f"Dataset '{dataset_name}' not found in the database. "
                "Ensure that the dataset has been loaded into the database."
            )
        return query_dataset_record_count(
            connection=self.connection,
            dataset_name=dataset_name,
            key_type=self.dataset_key_types[dataset_name],
        )

    def dataset_record_count(self, dataset_name: str) -> int:
        """Return cached record count for one dataset.

        Args:
            dataset_name: Dataset name to count.

        Returns:
            Number of stored records for the dataset.

        Raises:
            ValueError: If the dataset is unknown.
        """
        if dataset_name not in self.dataset_record_counts:
            raise ValueError(
                f"Dataset '{dataset_name}' not found in the database. "
                "Ensure that the dataset has been loaded into the database."
            )
        return self.dataset_record_counts[dataset_name]

    def get_int_records(
        self, dataset_name: str, record_keys: set[int] | None = None
    ) -> Iterable[IntKeyedRecord]:
        """Yield deserialized records for an integer-keyed dataset.

        Args:
            dataset_name: Dataset name to query.
            record_keys: Optional integer-key filter. When ``None``, all records
                for the dataset are yielded.

        Yields:
            ``(record_key, record)`` tuples for matching records.

        Raises:
            ValueError: If dataset is unknown or not integer-keyed.
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
    ) -> Iterable[StrKeyedRecord]:
        """Yield deserialized records for a string-keyed dataset.

        Args:
            dataset_name: Dataset name to query.
            record_keys: Optional string-key filter. When ``None``, all records
                for the dataset are yielded.

        Yields:
            ``(record_key, record)`` tuples for matching records.

        Raises:
            ValueError: If dataset is unknown or not string-keyed.
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

    def get_int_records_page(
        self, dataset_name: str, *, limit: int, offset: int
    ) -> Iterable[IntKeyedRecord]:
        """Yield a page of records for an integer-keyed dataset.

        Args:
            dataset_name: Dataset name to query.
            limit: Maximum number of records to return.
            offset: Starting offset for pagination.

        Yields:
            ``(record_key, record)`` tuples for the requested page.

        Raises:
            ValueError: If dataset is unknown or not integer-keyed.
        """
        if dataset_name not in self.dataset_key_types:
            raise ValueError(
                f"Dataset '{dataset_name}' not found in the database. "
                "Ensure that the dataset has been loaded into the database."
            )
        if self.dataset_key_types[dataset_name] != "int":
            raise ValueError(
                f"Dataset '{dataset_name}' does not have integer keys. "
                "Use get_str_records_page for datasets with string keys."
            )
        for record in query_int_records_page(
            connection=self.connection,
            dataset_name=dataset_name,
            serialization_format=self.serialization_format,
            limit=limit,
            offset=offset,
        ):
            yield record.record_key, record.deserialize_record()

    def get_str_records_page(
        self, dataset_name: str, *, limit: int, offset: int
    ) -> Iterable[StrKeyedRecord]:
        """Yield a page of records for a string-keyed dataset.

        Args:
            dataset_name: Dataset name to query.
            limit: Maximum number of records to return.
            offset: Starting offset for pagination.

        Yields:
            ``(record_key, record)`` tuples for the requested page.

        Raises:
            ValueError: If dataset is unknown or not string-keyed.
        """
        if dataset_name not in self.dataset_key_types:
            raise ValueError(
                f"Dataset '{dataset_name}' not found in the database. "
                "Ensure that the dataset has been loaded into the database."
            )
        if self.dataset_key_types[dataset_name] != "str":
            raise ValueError(
                f"Dataset '{dataset_name}' does not have string keys. "
                "Use get_int_records_page for datasets with integer keys."
            )
        for record in query_str_records_page(
            connection=self.connection,
            dataset_name=dataset_name,
            serialization_format=self.serialization_format,
            limit=limit,
            offset=offset,
        ):
            yield record.record_key, record.deserialize_record()

    @staticmethod
    def as_dict(keyed_records: Iterable[KeyedRecord]) -> Dataset:
        """Convert an iterable of keyed records into a dataset mapping.

        Args:
            keyed_records: Iterable of ``(record_key, record)`` tuples.

        Returns:
            Dictionary keyed by record key.
        """
        return {record_key: record for record_key, record in keyed_records}
