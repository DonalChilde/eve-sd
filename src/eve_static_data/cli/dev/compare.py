"""Compare the records from the file version and the database version of the SDE."""

from pathlib import Path
from typing import Annotated, Any, cast

import typer
from rich.console import Console

from eve_static_data.db.helpers import create_read_write_connection
from eve_static_data.db.query import DatasetDbQuery
from eve_static_data.helpers import json_io, yaml_io
from eve_static_data.helpers.sde_metadata import load_sde_metadata

app = typer.Typer(
    no_args_is_help=True, help="Compare SDE records between file and database."
)


@app.command()
def compare(
    sde_path: Annotated[
        Path, typer.Argument(help="Path to the SDE directory containing JSONL files.")
    ],
    db_path: Annotated[Path, typer.Argument(help="Path to the database file.")],
) -> None:
    file_sde_metadata = load_sde_metadata(sde_path)
    with create_read_write_connection(str(db_path)) as connection:
        db_query = DatasetDbQuery(connection)
        db_sde_metadata = db_query.sde_metadata
        if db_sde_metadata is None:
            raise ValueError(
                "SDE metadata not found in the database. Ensure that the database has been initialized with SDE metadata."
            )
        if (
            not file_sde_metadata.buildNumber == db_sde_metadata.buildNumber
            and file_sde_metadata.releaseDate == db_sde_metadata.releaseDate
            and file_sde_metadata.source_format == db_sde_metadata.source_format
        ):
            raise ValueError(
                "SDE metadata mismatch between file and database. "
                f"File metadata: {file_sde_metadata}, Database metadata: {db_sde_metadata}"
            )
        console = Console()
        console.print(
            "[bold green]SDE metadata matches between file and database.[/bold green]"
        )
        if file_sde_metadata.source_format == "jsonl-model":
            files = list(sde_path.glob("*.jsonl"))
        else:
            files = list(sde_path.glob("*.yaml"))
        files.sort(key=lambda f: f.stem)
        file_dataset_names = {file.stem for file in files}
        db_dataset_names = set(db_query.dataset_key_types.keys())
        if file_dataset_names != db_dataset_names:
            raise ValueError(
                "Dataset names mismatch between file and database. "
                f"File datasets: {file_dataset_names}, Database datasets: {db_dataset_names}"
            )
        for dataset_name in file_dataset_names:
            console.print(f"[bold blue]Comparing dataset: {dataset_name}[/bold blue]")
            if file_sde_metadata.source_format == "jsonl-model":
                file_records = json_io.jsonl_load_path(
                    sde_path / f"{dataset_name}.jsonl"
                )
                file_records = {record["_key"]: record for record in file_records}
            else:
                file_records = yaml_io.safe_load_path(sde_path / f"{dataset_name}.yaml")
            cast(dict[str | int, dict[str | int, Any]], file_records)
            match db_query.dataset_key_types[dataset_name]:
                case "int":
                    db_records = {
                        record_key: record
                        for record_key, record in db_query.get_int_records(dataset_name)
                    }
                case "str":
                    db_records = {
                        record_key: record
                        for record_key, record in db_query.get_str_records(dataset_name)
                    }
                case _:
                    raise ValueError(
                        f"Unexpected key type for dataset {dataset_name}: {db_query.dataset_key_types[dataset_name]}"
                    )
            if set(file_records.keys()) != set(db_records.keys()):
                raise ValueError(
                    f"Record keys mismatch for dataset {dataset_name}. "
                    f"File keys: {set(file_records.keys())}, Database keys: {set(db_records.keys())}"
                )
            if len(file_records) != len(db_records):
                raise ValueError(
                    f"Record count mismatch for dataset {dataset_name}. "
                    f"File records: {len(file_records)}, Database records: {len(db_records)}"
                )
            for record_key in file_records:
                if record_key not in db_records:
                    raise ValueError(
                        f"Record key {record_key} not found in database for dataset {dataset_name}."
                    )
                db_record = db_records[record_key]
                if file_records[record_key] != db_record:
                    raise ValueError(
                        f"Record mismatch for key {record_key} in dataset {dataset_name}. "
                        f"File record: {file_records[record_key]}, Database record: {db_record}"
                    )
            console.print(
                f"[bold green]Dataset {dataset_name} records match between file and database.[/bold green]"
            )
