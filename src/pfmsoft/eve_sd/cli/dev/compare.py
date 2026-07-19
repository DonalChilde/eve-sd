"""Compare local SDE source files against records stored in an SDE database."""

from pathlib import Path
from typing import Annotated, Any, cast

import typer
from pfmsoft.eve_snippets import json_io, yaml_io
from rich.console import Console

from pfmsoft.eve_sd import db_connection_manager
from pfmsoft.eve_sd.db.query import DatasetDbQuery
from pfmsoft.eve_sd.helpers.sde_metadata import SdeVariant, load_sde_metadata

app = typer.Typer(
    no_args_is_help=True, help="Compare SDE records between file and database."
)

# TODO: use raw loader helpers, record types
# TODO: define a report format, and use messenger/stdout framework
# - report can note load times for files vs database
# TODO: add args to support.


@app.command()
def compare(
    ctx: typer.Context,
    from_directory: Annotated[
        Path,
        typer.Option(
            "--from",
            help="The path to the directory containing the SDE dataset files.",
            exists=True,
            file_okay=False,
            dir_okay=True,
        ),
    ],
    with_file: Annotated[
        Path,
        typer.Option(
            "--to",
            help="The path to the SQLite database file.",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
        ),
    ],
) -> None:
    """Compare source dataset records to database records for each dataset."""
    file_sde_metadata = load_sde_metadata(from_directory)
    with db_connection_manager(with_file) as connection:
        db_query = DatasetDbQuery(connection)
        db_sde_metadata = db_query.sde_metadata
        if (
            not file_sde_metadata.buildNumber == db_sde_metadata.buildNumber
            and file_sde_metadata.releaseDate == db_sde_metadata.releaseDate
            and file_sde_metadata.variant == db_sde_metadata.variant
        ):
            raise ValueError(
                "SDE metadata mismatch between file and database. "
                f"File metadata: {file_sde_metadata}, Database metadata: {db_sde_metadata}"
            )
        console = Console()
        console.print(
            "[bold green]SDE metadata matches between file and database.[/bold green]"
        )
        if file_sde_metadata.variant == SdeVariant.JSONL:
            files = list(from_directory.glob("*.jsonl"))
        else:
            files = list(from_directory.glob("*.yaml"))
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
            if file_sde_metadata.variant == SdeVariant.JSONL:
                file_records = json_io.jsonl_load_path(
                    from_directory / f"{dataset_name}.jsonl"
                )
                file_records = {record["_key"]: record for record in file_records}
            else:
                file_records = yaml_io.safe_load_path(
                    from_directory / f"{dataset_name}.yaml"
                )
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
