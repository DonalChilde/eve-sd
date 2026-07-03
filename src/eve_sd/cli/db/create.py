"""Create an SDE SQLite database from local JSONL or YAML datasets."""

import logging
import sqlite3
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter_ns
from typing import Annotated

import typer
from rich.console import Console
from rich.progress import (
    FileSizeColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TotalFileSizeColumn,
)

from eve_sd import KeyedRecord, db_connection_manager
from eve_sd.db.helpers import write_key_types
from eve_sd.db.load_datasets import (
    get_key_type_from_records,
    write_db_metadata,
    write_sde_records_to_db,
)
from eve_sd.db.models import SerializationFormat
from eve_sd.helpers import yaml_io
from eve_sd.helpers.load_raw_datasets import load_jsonl_as_records
from eve_sd.helpers.sde_metadata import load_sde_metadata

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
    with db_connection_manager(db_path, read_only=False) as connection:
        start_time_ns = perf_counter_ns()
        match sde_metadata.variant:
            case "jsonl":
                if serialization_format is None:
                    serialization_format = SerializationFormat.JSON
                files = list(from_directory.glob("*.jsonl"))
                results = _load_jsonl_files_to_db(
                    jsonl_files=files,
                    connection=connection,
                    serialization_format=serialization_format,
                    messenger=messenger,
                )
            case "yaml":
                if serialization_format is None:
                    serialization_format = SerializationFormat.PICKLE
                results = _load_yaml_files_to_db(
                    yaml_files=list(from_directory.glob("*.yaml")),
                    connection=connection,
                    serialization_format=serialization_format,
                    messenger=messenger,
                )
            case _:
                messenger.print(
                    f"[bold red]Error:[/bold red] Unsupported SDE variant: {sde_metadata.variant}. Supported variants are 'jsonl' and 'yaml'."
                )
                raise typer.Exit(code=1)
        # use results to write dataset keytype table
        key_types = {result.dataset_name: result.key_type for result in results}
        write_key_types(connection, dataset_key_types=key_types)
        write_db_metadata(
            connection,
            sde_metadata=sde_metadata,
            serialization_format=serialization_format,
        )
    end_time_ns = perf_counter_ns()
    elapsed_time_s = (end_time_ns - start_time_ns) / 1_000_000_000
    total_records = sum(result.record_count for result in results)
    total_datasets = len(results)
    messenger.print(
        f"[bold green]Successfully imported SDE data into database at {db_path} in {elapsed_time_s:.2f} seconds.[/bold green]"
    )
    messenger.print(
        f"[bold green]Imported {total_records} records across {total_datasets} datasets.[/bold green]"
    )
    messenger.print(results)


@dataclass(slots=True, kw_only=True)
class DatasetImportResult:
    dataset_name: str
    record_count: int
    key_type: str


def _jsonl_file_as_records(
    jsonl_file: Path,
) -> tuple[str, Iterable[KeyedRecord]]:
    dataset_name = jsonl_file.stem
    records = load_jsonl_as_records(jsonl_file)
    return dataset_name, records


def _yaml_file_as_records(
    yaml_file: Path,
) -> tuple[str, Iterable[KeyedRecord]]:
    dataset_name = yaml_file.stem
    records_dict = yaml_io.safe_load_path(yaml_file)
    records = (
        (record_key, record_value) for record_key, record_value in records_dict.items()
    )
    return dataset_name, records


def _load_records_to_db(
    dataset_name: str,
    records: Iterable[KeyedRecord],
    connection: sqlite3.Connection,
    serialization_format: SerializationFormat,
) -> DatasetImportResult:
    key_type, records = get_key_type_from_records(
        records=records, dataset_name=dataset_name
    )
    count = write_sde_records_to_db(
        connection=connection,
        dataset_name=dataset_name,
        records=records,
        key_type=key_type,
        serialization_format=serialization_format,
    )
    return DatasetImportResult(
        dataset_name=dataset_name, record_count=count, key_type=key_type
    )


def _load_jsonl_files_to_db(
    jsonl_files: list[Path],
    connection: sqlite3.Connection,
    serialization_format: SerializationFormat,
    messenger: Console,
) -> list[DatasetImportResult]:
    """Load JSONL files from the SDE data directory into the database."""
    results: list[DatasetImportResult] = []
    files_with_sizes: list[tuple[Path, int]] = [
        (file, file.stat().st_size) for file in jsonl_files
    ]
    total_size = sum(size for _, size in files_with_sizes)
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TextColumn("[progress.data]{task.fields[filename]}"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        FileSizeColumn(),
        TotalFileSizeColumn(),
        transient=True,
        console=messenger,
    ) as progress:
        task = progress.add_task(
            description="Importing JSONL files into database...",
            total=total_size,
            filename="",
        )
        for jsonl_file, size in files_with_sizes:
            progress.update(task, advance=size, filename=jsonl_file.name)
            dataset_name, records = _jsonl_file_as_records(jsonl_file)
            result = _load_records_to_db(
                dataset_name=dataset_name,
                records=records,
                connection=connection,
                serialization_format=serialization_format,
            )
            results.append(result)
    return results


def _load_yaml_files_to_db(
    yaml_files: list[Path],
    connection: sqlite3.Connection,
    serialization_format: SerializationFormat,
    messenger: Console,
) -> list[DatasetImportResult]:
    """Load YAML files from the SDE data directory into the database."""
    results: list[DatasetImportResult] = []
    files_with_sizes: list[tuple[Path, int]] = [
        (file, file.stat().st_size) for file in yaml_files
    ]
    total_size = sum(size for _, size in files_with_sizes)
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TextColumn("[progress.data]{task.fields[filename]}"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        FileSizeColumn(),
        TotalFileSizeColumn(),
        transient=True,
        console=messenger,
    ) as progress:
        task = progress.add_task(
            description="Importing YAML files into database...",
            total=total_size,
            filename="",
        )
        for yaml_file, size in files_with_sizes:
            progress.update(task, advance=size, filename=yaml_file.name)
            dataset_name, records = _yaml_file_as_records(yaml_file)
            result = _load_records_to_db(
                dataset_name=dataset_name,
                records=records,
                connection=connection,
                serialization_format=serialization_format,
            )
            results.append(result)
    return results
