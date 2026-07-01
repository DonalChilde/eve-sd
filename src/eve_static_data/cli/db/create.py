"""CLI command to import SDE data from JSONL files into the database."""

import logging
from pathlib import Path
from time import perf_counter_ns
from typing import Annotated

import typer
from rich.console import Console

from eve_static_data.db.helpers import create_read_write_connection
from eve_static_data.db.load_jsonl_datasets import import_jsonl_sde_to_db
from eve_static_data.db.load_yaml_datasets import import_yaml_sde_to_db
from eve_static_data.db.models_2 import SerializationFormat
from eve_static_data.helpers.sde_metadata import load_sde_metadata

logger = logging.getLogger(__name__)
app = typer.Typer(no_args_is_help=True)


@app.command()
def create(
    ctx: typer.Context,
    from_directory: Annotated[
        Path,
        typer.Option(
            "--from",
            help="The path to the SDE data directory containing the SDE files.",
            exists=True,
            dir_okay=True,
        ),
    ],
    to_directory: Annotated[
        Path,
        typer.Option(
            "--to",
            help="The directory to save the SQLite database file to.",
            file_okay=False,
            dir_okay=True,
        ),
    ],
    file_name: Annotated[
        str | None,
        typer.Option(
            "--file-name",
            help="The name of the SQLite database file to create. defaults to None, "
            "which will create a file named `eve_static_data_{build_number}_{variant}.db`",
            show_default=True,
        ),
    ] = None,
    serialization_format: Annotated[
        SerializationFormat | None,
        typer.Option(
            "-f",
            "--serialization-format",
            help="The serialization format to use for storing records in the database. "
            "If not provided, the serialization format will be determined based on the "
            "SDE variant. JSONL will be `json` and YAML will be `pickle`.",
            case_sensitive=False,
            show_default=True,
        ),
    ] = None,
    overwrite: Annotated[
        bool,
        typer.Option(
            "-o",
            "--overwrite",
            help="Whether to overwrite the database if it already exists.",
        ),
    ] = False,
    quiet: Annotated[
        bool,
        typer.Option(
            "--quiet",
            help="Suppress output messages.",
        ),
    ] = False,
):
    """Import SDE data from JSONL or YAML files into the database."""
    if quiet:
        messenger = Console(stderr=True, quiet=True)
    else:
        messenger = Console(stderr=True)
    sde_metadata = load_sde_metadata(from_directory)
    messenger.print(f"[bold green]Found SDE metadata: {sde_metadata}[/bold green]")
    if file_name is None:
        file_name = f"eve_static_data_{sde_metadata.buildNumber}_{sde_metadata.variant.value}.db"
    db_path = to_directory / file_name

    if db_path.exists() and not overwrite:
        messenger.print(
            f"[bold red]Error:[/bold red] Database file {db_path} already exists. Use --overwrite to overwrite it."
        )
        raise typer.Exit(code=1)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = create_read_write_connection(str(db_path.resolve()))
    start_time_ns = perf_counter_ns()
    match sde_metadata.variant:
        case "jsonl":
            if serialization_format is None:
                serialization_format = SerializationFormat.JSON
            import_jsonl_sde_to_db(
                from_directory,
                connection=connection,
                serialization_format=serialization_format,
            )
        case "yaml":
            if serialization_format is None:
                serialization_format = SerializationFormat.PICKLE
            import_yaml_sde_to_db(
                from_directory,
                connection=connection,
                serialization_format=serialization_format,
            )
        case _:
            messenger.print(
                f"[bold red]Error:[/bold red] Unsupported SDE variant: {sde_metadata.variant}. Supported variants are 'jsonl' and 'yaml'."
            )
            raise typer.Exit(code=1)
    end_time_ns = perf_counter_ns()
    elapsed_time_s = (end_time_ns - start_time_ns) / 1_000_000_000
    messenger.print(
        f"[bold green]Successfully imported SDE data into database at {db_path} in {elapsed_time_s:.2f} seconds.[/bold green]"
    )
