"""CLI command to convert SDE data from YAML format to JSON format."""

import json
from pathlib import Path
from time import perf_counter
from typing import Annotated

import typer
from rich.console import Console

from eve_static_data.helpers.yaml_loader import safe_load_IO
from eve_static_data.models.common import LangEnum, narrow_localizable_json_dict

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
    lang: Annotated[
        list[LangEnum] | None,
        typer.Option(
            "-l",
            "--lang",
            help="The one or more languages to include in the output JSON files. If not "
            "provided, all languages will be included.",
            show_default=True,
        ),
    ] = None,
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
                yaml_data = safe_load_IO(yaml_in)
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
                if lang:
                    yaml_data = narrow_localizable_json_dict(
                        yaml_data, set(lang.value for lang in lang)
                    )
                json.dump(yaml_data, json_out, ensure_ascii=False, indent=2)
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
