"""CLI command to convert SDE data from YAML format to JSON format."""

from pathlib import Path
from time import perf_counter
from typing import Annotated

import typer
from rich.console import Console

from eve_static_data.helpers import json_io, yaml_io

app = typer.Typer(no_args_is_help=True)


@app.command()
def yaml_to_json(
    yaml_sde_path: Annotated[
        Path,
        typer.Argument(
            help="The path to the SDE data directory containing the YAML files.",
            exists=True,
            dir_okay=True,
        ),
    ],
    json_output_path: Annotated[
        Path,
        typer.Argument(
            help="The path to the output JSON directory.",
            file_okay=False,
            dir_okay=True,
        ),
    ],
):
    """Convert SDE data from YAML format to JSON format."""
    console = Console()
    console.print("[bold green]Converting SDE Data from YAML to JSON[/bold green]")
    console.print(f"This will take several minutes.....")
    yaml_files = list(yaml_sde_path.glob("*.yaml"))
    yaml_files.sort()  # Sort the files alphabetically for consistent processing order
    if not yaml_files:
        console.print(
            f"[bold red]Error:[/bold red] No YAML files found in the specified SDE directory: {yaml_sde_path}"
        )
        raise typer.Exit(code=1)
    json_output_path.mkdir(parents=True, exist_ok=True)
    job_start = perf_counter()
    for yaml_file in yaml_files:
        console.print(f"Found YAML file: {yaml_file}")
        start = perf_counter()
        json_file_path = json_output_path / (yaml_file.stem + ".json")
        with (
            yaml_file.open("r", encoding="utf-8") as yaml_in,
            json_file_path.open("w", encoding="utf-8") as json_out,
        ):
            try:
                yaml_data = yaml_io.safe_load_IO(yaml_in)
                console.print(
                    f"Successfully read YAML file: {yaml_file} in {perf_counter() - start:.2f} seconds"
                )
            except Exception as e:
                console.print(
                    f"[bold red]Error:[/bold red] Failed to read YAML file {yaml_file}: {e}"
                )
                raise typer.Exit(code=1) from e
            start_json = perf_counter()
            try:
                json_out.write(
                    json_io.json_dumps(yaml_data, ensure_ascii=False, indent=2)
                )
                console.print(
                    f"Converted {yaml_file} to {json_file_path} in {perf_counter() - start_json:.2f} seconds"
                )
            except Exception as e:
                console.print(
                    f"[bold red]Error:[/bold red] Failed to write JSON file {json_file_path}: {e}"
                )
                raise typer.Exit(code=1) from e
            console.print(
                f"Finished processing {yaml_file} in {perf_counter() - start:.2f} seconds\n"
            )
    console.print(
        f"Finished converting all {len(yaml_files)} YAML files to JSON in {perf_counter() - job_start:.2f} seconds"
    )
