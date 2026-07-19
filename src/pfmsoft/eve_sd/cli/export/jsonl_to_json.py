"""Convert local SDE JSONL datasets into JSON files."""

from enum import StrEnum
from pathlib import Path
from time import perf_counter
from typing import Annotated

import typer
from rich.console import Console

from pfmsoft.eve_sd.helpers import json_io
from pfmsoft.eve_sd.helpers.save_text_file import save_text_file

app = typer.Typer(no_args_is_help=True)


class ContainerChoice(StrEnum):
    """Supported JSON output container shapes."""

    LIST = "list"
    DICT = "dict"


@app.command()
def jsonl_to_json(
    ctx: typer.Context,
    from_directory: Annotated[
        Path,
        typer.Option(
            "--from",
            help="The path to the SDE data directory containing the JSONL files.",
            exists=True,
            dir_okay=True,
        ),
    ],
    to_directory: Annotated[
        Path,
        typer.Option(
            "--to",
            help="The path to the output JSON directory.",
            file_okay=False,
            dir_okay=True,
        ),
    ],
    container: Annotated[
        ContainerChoice,
        typer.Option(
            "--container",
            help="The container type for the output JSON files.",
            show_default=True,
        ),
    ] = ContainerChoice.DICT,
    overwrite: Annotated[
        bool,
        typer.Option(
            "--overwrite", help="Whether to overwrite existing files", show_default=True
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
    """Convert SDE datasets from JSONL format to JSON format.

    Output can be written either as a list of records or as a dictionary keyed
    by each record's ``_key`` field.
    """
    if quiet:
        messenger = Console(stderr=True, quiet=True)
    else:
        messenger = Console(stderr=True)
    jsonl_files = list(from_directory.glob("*.jsonl"))
    jsonl_files.sort()  # Sort the files alphabetically for consistent processing order
    if not jsonl_files:
        messenger.print(
            f"[bold red]Error:[/bold red] No JSONL files found in the specified SDE directory: {from_directory}"
        )
        raise typer.Exit(code=1)
    messenger.print(
        f"[bold green]Converting SDE Data from JSONL to JSON ({container.value}s)[/bold green]"
    )
    for jsonl_file in jsonl_files:
        json_file_name = jsonl_file.with_suffix(".json").name
        target_file = to_directory / json_file_name
        # Before loading the JSONL file, check if the target JSON file already exists and handle overwrite logic
        if not overwrite and target_file.exists():
            messenger.print(
                f"[bold red]Error:[/bold red] Fixture output already exists for {target_file.name}. "
                "Use --overwrite to replace existing files."
            )
            raise typer.Exit(code=1)
        loaded = json_io.jsonl_load_path(jsonl_file)
        start_jsonl = perf_counter()
        match container:
            case ContainerChoice.LIST:
                marshalled_data = list(loaded)
            case ContainerChoice.DICT:
                marshalled_data = {record["_key"]: record for record in loaded}
        end_jsonl = perf_counter()
        messenger.print(
            f"Successfully read JSONL file: {jsonl_file.name} in {end_jsonl - start_jsonl:.2f} seconds"
        )

        try:
            start_json = perf_counter()
            save_text_file(
                text=json_io.json_dumps(marshalled_data, indent=2),
                output_directory=target_file.parent,
                file_name=target_file.name,
                overwrite=overwrite,
            )
            end_json = perf_counter()
            messenger.print(
                f"Successfully converted {jsonl_file.name} to {target_file.name} in {end_json - start_json:.2f} seconds"
            )
        except Exception as e:
            messenger.print(
                f"[bold red]Error:[/bold red] Failed to convert {jsonl_file.name} to JSON: {e}"
            )
            raise typer.Exit(code=1) from e
