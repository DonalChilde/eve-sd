"""Run ad-hoc performance checks against a local SDE SQLite database."""

from pathlib import Path
from time import perf_counter
from typing import Annotated

import typer
from rich.console import Console

from eve_sd.db.helpers import create_read_write_connection
from eve_sd.db.query import DatasetDbQuery

app = typer.Typer(no_args_is_help=True, help="Database performance testing commands.")


# TODO: define a report format, and use messenger/stdout framework
# TODO: add args to support.
@app.command()
def db_perf(
    ctx: typer.Context,
    from_file: Annotated[
        Path,
        typer.Option(
            "--from",
            help="The path to the SQLite database file.",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
        ),
    ],
) -> None:
    """Measure query performance by loading all records from each dataset."""
    job_start = perf_counter()
    with create_read_write_connection(str(from_file)) as connection:
        console = Console()
        console.print(
            f"[bold green]Testing database performance for {from_file}[/bold green]"
        )
        console.print("Querying all datasets and measuring time taken...")
        db_query = DatasetDbQuery(connection)
        dataset_key_types = db_query.dataset_key_types
        serialization_format = db_query.serialization_format
        console.print(
            f"Serialization format used in the database: {serialization_format}"
        )
        for dataset_name, key_type in dataset_key_types.items():
            console.print(
                f"Querying dataset '{dataset_name}' with key type '{key_type}'..."
            )
            if key_type == "int":
                start = perf_counter()
                records = list(db_query.get_int_records(dataset_name))
                end = perf_counter()

            elif key_type == "str":
                start = perf_counter()
                records = list(db_query.get_str_records(dataset_name))
                end = perf_counter()
            else:
                raise ValueError(
                    f"Unexpected key type '{key_type}' for dataset '{dataset_name}'."
                )
            console.print(
                f"Retrieved {len(records)} records from dataset '{dataset_name}' in {end - start:.4f} seconds."
            )
    job_end = perf_counter()
    console.print(
        f"[bold green]Database performance test completed in {job_end - job_start:.4f} seconds.[/bold green]"
    )
