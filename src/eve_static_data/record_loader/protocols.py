"""Protocol definitions for loader classes that load dataset records.

This is not the most efficient way to load records for all sources, but it provides a
common interface for different loader implementations. The protocol defines methods for
loading records and raw records, as well as retrieving SDE metadata.

Some sources will have to load an entire dataset into memory to filter records by key,
while others may be able to load records one by one. The protocol allows for a common
interface no matter the underlying implementation.

Because the DatasetRecordBase subclasses are deserialized from the raw records using Pydantic,
the load_records method inherently provides validation of the raw records.
load_raw_records provides no validation.
"""

from collections.abc import Iterable
from typing import Any, Protocol, TypeVar

from eve_static_data.helpers.sde_metadata import SdeMetadata
from eve_static_data.models.common import DatasetRecordBase
from eve_static_data.models.dataset_filenames import SdeDatasets

T = TypeVar("T", bound=DatasetRecordBase)


class LoaderProtocol(Protocol):
    """Protocol for loader classes that load dataset records."""

    def load_records[T: DatasetRecordBase](
        self, record_model: type[T], *, record_keys: set[int | str] | None = None
    ) -> Iterable[tuple[int | str, T]]:
        """Load records from a dataset.

        The dataset is determined by the record_model's dataset attribute. If record_keys
        is provided, only records with those keys will be loaded.

        Record instances are created by deserializing the raw records using Pydantic,
        which provides validation of the raw records. If a raw record fails validation,
        a ValidationError will be raised.

        Args:
            record_model (type[T]): A subclass of a DatasetRecordBase subclass that specifies
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
        ...

    def load_raw_records(
        self, dataset: SdeDatasets, *, record_keys: set[int | str] | None = None
    ) -> Iterable[tuple[int | str, dict[str, Any]]]:
        """Load raw records from a dataset file.

        The dataset is determined by the dataset argument. If record_keys is provided,
        only records with those keys will be loaded.

        Raw records are returned as dictionaries without any validation. If a record is
        missing a required field or has an invalid type, it will be returned as-is.

        Args:
            dataset (SdeDatasets): The dataset to load.
            record_keys (set[int | str] | None): Optional set of keys to filter the
                records. If None, all records will be loaded.

        Returns:
            Iterable[tuple[int | str, dict[str, Any]]]: An iterable of tuples, each containing a
                record key and the corresponding raw record as a dictionary.
        """
        ...

    def sde_metadata(self) -> SdeMetadata:
        """Return metadata about the SDE."""
        ...
