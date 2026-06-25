"""Validate the SDE data."""

import json
from dataclasses import asdict
from enum import Enum
from pathlib import Path
from typing import Annotated, cast

import typer
from rich.console import Console

from eve_static_data.helpers.save_text_file import save_text_file
from eve_static_data.validation.markdown_report import generate_markdown_report
from eve_static_data.validation.validation_from_files import validate_sde_yaml_datasets

app = typer.Typer(no_args_is_help=True)


def _json_default(value: object) -> object:
    """Convert non-JSON-native validation summary values to serializable forms."""
    if isinstance(value, set):
        typed_value = cast(set[object], value)
        return sorted(str(item) for item in typed_value)
    if isinstance(value, Enum):
        return value.value
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


@app.command(name="yaml-files")
def yaml_model(
    ctx: typer.Context,
    sde_path: Annotated[
        Path,
        typer.Argument(
            help="The path to the yaml SDE data.",
        ),
    ],
    report_path: Annotated[
        Path | None,
        typer.Option(
            "--report-path",
            help="The directory path to save the validation report json and markdown to. If not provided, "
            "the markdown report output will be output to the terminal.",
            file_okay=False,
            dir_okay=True,
        ),
    ] = None,
    overwrite: Annotated[
        bool,
        typer.Option(
            "--overwrite",
            help="Whether to overwrite existing validation reports.",
        ),
    ] = False,
):
    """Validate the SDE YAML datasets.

    Validates the yaml-format datasets in the given SDE path and outputs a summary of
    the validation results.

    If a report path is provided, the validation summary will be saved as a JSON and
    Markdown report in the specified directory. If no report path is provided, the
    validation summary will be printed to the terminal in Markdown format.
    """
    console = Console()
    console.print("[bold green]Validating SDE YAML Datasets[/bold green]")
    summary = validate_sde_yaml_datasets(sde_path)
    markdown_report = generate_markdown_report(summary)

    if report_path is None:
        console.print(markdown_report)
        return

    build_suffix = str(summary.sde_metadata.buildNumber)
    save_text_file(
        text=json.dumps(asdict(summary), indent=2, default=_json_default),
        output_path=report_path,
        file_name=f"yaml_validation_result_{build_suffix}.json",
        overwrite=overwrite,
    )
    save_text_file(
        text=markdown_report,
        output_path=report_path,
        file_name=f"yaml_validation_report_{build_suffix}.md",
        overwrite=overwrite,
    )
    console.print(f"Saved validation reports to {report_path}")
