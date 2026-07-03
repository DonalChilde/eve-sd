import sqlite3
from collections.abc import Iterable

from eve_sd.db.query import DatasetDbQuery
from eve_sd.helpers.schema_report.schema_report import (
    DatasetInput,
    SchemaReport,
    build_schema_report,
)


def get_schema_report_from_db(connection: sqlite3.Connection) -> SchemaReport:
    """Generate a schema report from all datasets in a sqlite database."""
    db_query = DatasetDbQuery(connection)
    sde_metadata = db_query.sde_metadata
    if sde_metadata is None:
        raise ValueError("SDE metadata not found in the database.")

    def dataset_input_generator() -> Iterable[DatasetInput]:
        for dataset_name, key_type in db_query.dataset_key_types.items():
            if key_type == "int":
                data = db_query.get_int_records(dataset_name)
            elif key_type == "str":
                data = db_query.get_str_records(dataset_name)
            else:
                raise ValueError(
                    f"Unexpected key type '{key_type}' for dataset '{dataset_name}'."
                )
            yield DatasetInput(
                dataset_name=dataset_name,
                dataset_data={k: v for k, v in data},
                sde_metadata=sde_metadata,
            )

    return build_schema_report(
        datasets=dataset_input_generator(),
        sde_metadata=sde_metadata,
        dataset_source=str(connection),
    )
