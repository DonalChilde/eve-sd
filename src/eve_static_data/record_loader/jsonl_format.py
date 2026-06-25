"""Loader for loading SDE records from jsonl-format sources."""

import logging
import sqlite3
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from eve_static_data.helpers.load_raw_datasets import load_dataset_from_file
from eve_static_data.helpers.sde_metadata import (
    SdeMetadata,
    load_sde_metadata,
    load_sde_metadata_from_sqlite,
)
from eve_static_data.models.common import DatasetRecordBase
from eve_static_data.models.dataset_filenames import SdeDatasets
from eve_static_data.record_loader.protocols import LoaderProtocol

logger = logging.getLogger(__name__)


class JsonlFileLoader(LoaderProtocol):
    def __init__(self, sde_path: Path):
        """Initialize the loader with the path to the SDE directory."""
        self._sde_path = sde_path
        self._sde_metadata: SdeMetadata | None = None

    def sde_metadata(self) -> SdeMetadata:
        """Get the SDE metadata, loading it from the SDE path if necessary."""
        if self._sde_metadata is None:
            self._sde_metadata = load_sde_metadata(self._sde_path)
        return self._sde_metadata

    def load_records[T: DatasetRecordBase](
        self,
        record_model: type[T],
        *,
        record_keys: set[int | str] | None = None,
    ) -> Iterable[tuple[int | str, T]]:
        """Load records from a dataset.

        The dataset is determined by the record_model's dataset attribute. If record_keys
        is provided, only records with those keys will be loaded.

        Record instances are created by deserializing the raw records using Pydantic,
        which provides validation of the raw records. If a raw record fails validation,
        a ValidationError will be raised.

        Args:
            record_model (type[T]): A subclass of DatasetRecordBase that specifies
                the dataset to load.
            record_keys (set[int | str] | None): Optional set of keys to filter the
                records. If None, all records will be loaded.

        Returns:
            Iterable[tuple[int | str, T]]: An iterable of tuples, each containing a
                record key and the corresponding record instance.

        Raises:
            ValidationError: If a raw record fails validation when deserializing into
                the record_model.
        """
        raise NotImplementedError("Record models not yet available for jsonl format.")

    def load_raw_records(
        self,
        dataset: SdeDatasets,
        *,
        record_keys: set[int | str] | None = None,
    ) -> Iterable[tuple[int | str, dict[str, Any]]]:
        """Load raw records from a dataset.

        The dataset is specified by the dataset parameter. If record_keys is provided,
        only records with those keys will be loaded.

        Args:
            dataset (SdeDatasets): The dataset to load.
            record_keys (set[int | str] | None): Optional set of keys to filter the
                records. If None, all records will be loaded.

        Returns:
            Iterable[tuple[int | str, dict[str, Any]]]: An iterable of tuples, each
                containing a record key and the corresponding raw record dictionary.
        """
        dataset_dict, source_format = load_dataset_from_file(
            dataset, sde_path=self._sde_path
        )
        if source_format != "jsonl-model":
            raise ValueError(
                f"Expected a JSONL mapping (dict) in file '{dataset.value}', but got {source_format}."
            )
        # log request for keys that are not present in the dataset
        if record_keys is not None:
            missing_keys = record_keys - dataset_dict.keys()
            if missing_keys:
                logger.warning(
                    f"Requested record keys {missing_keys} not found in dataset '{dataset.value}'."
                )
        for key, record in dataset_dict.items():
            if record_keys is None or key in record_keys:
                yield key, record


class JsonlDBLoader(LoaderProtocol):
    def __init__(self, connection: sqlite3.Connection):
        """Initialize the loader with a SQLite database connection."""
        self._connection = connection
        self._sde_metadata: SdeMetadata | None = None

    def sde_metadata(self) -> SdeMetadata:
        """Get the SDE metadata, loading it from the database if necessary."""
        if self._sde_metadata is None:
            self._sde_metadata = load_sde_metadata_from_sqlite(self._connection)
        return self._sde_metadata

    def load_records[T: DatasetRecordBase](
        self,
        record_model: type[T],
        *,
        record_keys: set[int | str] | None = None,
    ) -> Iterable[tuple[int | str, T]]:
        """Load records from a dataset.

        The dataset is determined by the record_model's dataset attribute. If record_keys
        is provided, only records with those keys will be loaded.

        Record instances are created by deserializing the raw records using Pydantic,
        which provides validation of the raw records. If a raw record fails validation,
        a ValidationError will be raised.

        Args:
            record_model (type[T]): A subclass of DatasetRecordBase that specifies
                the dataset to load.
            record_keys (set[int | str] | None): Optional set of keys to filter the
                records. If None, all records will be loaded.

        Returns:
            Iterable[tuple[int | str, T]]: An iterable of tuples, each containing a
                record key and the corresponding record instance.

        Raises:
            ValidationError: If a raw record fails validation when deserializing into
                the record_model.
        """
        raise NotImplementedError("Record models not yet available for jsonl format.")

    def load_raw_records(
        self,
        dataset: SdeDatasets,
        *,
        record_keys: set[int | str] | None = None,
    ) -> Iterable[tuple[int | str, dict[str, Any]]]:
        """Load raw records from a dataset.

        The dataset is specified by the dataset parameter. If record_keys is provided,
        only records with those keys will be loaded.

        Args:
            dataset (SdeDatasets): The dataset to load.
            record_keys (set[int | str] | None): Optional set of keys to filter the
                records. If None, all records will be loaded.

        Returns:
            Iterable[tuple[int | str, dict[str, Any]]]: An iterable of tuples, each
                containing a record key and the corresponding raw record dictionary.
        """
        raise NotImplementedError("Raw records not yet available for jsonl format.")
