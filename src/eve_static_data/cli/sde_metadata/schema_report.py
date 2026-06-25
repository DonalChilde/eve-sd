from pathlib import Path
from typing import Annotated

import typer

from eve_static_data.helpers import json_io
from eve_static_data.helpers.save_text_file import save_text_file
from eve_static_data.helpers.schema_report.markdown_report import (
    generate_markdown_report,
)
from eve_static_data.helpers.schema_report.report_from_files import (
    get_yaml_schema_report,
)

app = typer.Typer(no_args_is_help=True)


@app.command(name="report-files")
def report_files(
    ctx: typer.Context,
    sde_path: Annotated[
        Path,
        typer.Argument(
            help="The path to the SDE data files.",
        ),
    ],
    report_path: Annotated[
        Path | None,
        typer.Option(
            "--report-path",
            help="The directory path to save the schema report json and markdown to. If not provided, "
            "the markdown report output will be output to the terminal.",
            file_okay=False,
            dir_okay=True,
        ),
    ] = None,
    overwrite: Annotated[
        bool,
        typer.Option(
            "--overwrite",
            help="Whether to overwrite existing schema reports.",
        ),
    ] = False,
) -> None:
    """Generate a schema report from the SDE data files.

    Generates a schema report from the datasets in the given SDE path and outputs a summary of
    the schema report.
    """
    schema_report = get_yaml_schema_report(sde_path)
    markdown_report = generate_markdown_report(schema_report)

    if report_path:
        json_file = report_path / "schema_report.json"
        markdown_file = report_path / "schema_report.md"

        save_text_file(
            text=json_io.json_dumps(schema_report, indent=2),
            output_path=report_path,
            file_name=json_file.name,
            overwrite=overwrite,
        )
        save_text_file(
            text=markdown_report,
            output_path=report_path,
            file_name=markdown_file.name,
            overwrite=overwrite,
        )
    else:
        typer.echo(markdown_report)
