"""Convert local SDE YAML datasets into JSON files."""

from pathlib import Path
from time import perf_counter
from typing import Annotated

import typer
from rich.console import Console

from eve_static_data.helpers import json_io, yaml_io
from eve_static_data.helpers.save_text_file import save_text_file

app = typer.Typer(no_args_is_help=True)


@app.command()
def yaml_to_json(
    from_directory: Annotated[
        Path,
        typer.Option(
            "--from",
            help="The path to the SDE data directory containing the YAML files.",
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
    """Convert SDE datasets from YAML format to JSON format.

    Note that integer mapping keys are serialized as strings because JSON object keys are
    always strings.
    """
    if quiet:
        messenger = Console(stderr=True, quiet=True)
    else:
        messenger = Console(stderr=True)

    messenger.print("[bold green]Converting SDE Data from YAML to JSON[/bold green]")
    messenger.print(f"This will take several minutes.....")
    yaml_files = list(from_directory.glob("*.yaml"))
    yaml_files.sort()  # Sort the files alphabetically for consistent processing order
    if not yaml_files:
        messenger.print(
            f"[bold red]Error:[/bold red] No YAML files found in the specified SDE directory: {from_directory}"
        )
        raise typer.Exit(code=1)
    to_directory.mkdir(parents=True, exist_ok=True)
    job_start = perf_counter()
    for yaml_file in yaml_files:
        start = perf_counter()
        json_file_name = yaml_file.stem + ".json"
        try:
            start_yaml = perf_counter()
            yaml_data = yaml_io.safe_load_path(yaml_file)
            end_yaml = perf_counter()
            messenger.print(
                f"Successfully read YAML file: {yaml_file.name} in {end_yaml - start_yaml:.2f} seconds"
            )
        except Exception as e:
            messenger.print(
                f"[bold red]Error:[/bold red] Failed to read YAML file {yaml_file.name}: {e}"
            )
            raise typer.Exit(code=1) from e
        start_json = perf_counter()
        try:
            save_text_file(
                text=json_io.json_dumps(yaml_data, indent=2) + "\n",
                output_directory=to_directory,
                file_name=json_file_name,
                overwrite=overwrite,
            )
            end_json = perf_counter()
            messenger.print(
                f"Converted {yaml_file.name} to {json_file_name} in {end_json - start_json:.2f} seconds"
            )
        except Exception as e:
            messenger.print(
                f"[bold red]Error:[/bold red] Failed to write JSON file {json_file_name}: {e}"
            )
            raise typer.Exit(code=1) from e
        messenger.print(
            f"Finished processing {yaml_file.name} in {perf_counter() - start:.2f} seconds\n"
        )
    messenger.print(
        f"Finished converting all {len(yaml_files)} YAML files to JSON in {perf_counter() - job_start:.2f} seconds"
    )
