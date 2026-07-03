"""Script to generate a schema report from SDE datasets in a directory."""

from enum import StrEnum
from pathlib import Path
from typing import Annotated

import typer

from eve_sd.helpers.json_io import json_dumps_path
from eve_sd.helpers.save_text_file import save_text_file
from eve_sd.helpers.schema_report.markdown_report import (
    generate_markdown_report,
)
from eve_sd.helpers.schema_report.report_from_files import (
    get_json_schema_report,
    get_jsonl_schema_report,
    get_yaml_schema_report,
)

app = typer.Typer(no_args_is_help=True)


class SdeFormatEnum(StrEnum):
    YAML_MODEL = "yaml-model"
    JSONL_MODEL = "jsonl-model"


@app.command()
def generate_report(
    sde_directory: Annotated[
        Path,
        typer.Argument(
            ...,
            exists=True,
            file_okay=False,
            dir_okay=True,
            readable=True,
            resolve_path=True,
        ),
    ],
    sde_format: Annotated[
        SdeFormatEnum | None,
        typer.Option(
            "--sde-format",
            help="The format of the SDE datasets. This is used to determine how to parse the files and may be included in the report metadata.",
        ),
    ] = None,
    output_path: Annotated[
        Path | None,
        typer.Option("-o", "--output-path", help="Path to write the markdown report."),
    ] = None,
    overwrite: Annotated[
        bool,
        typer.Option(
            "--overwrite",
            help="Whether to overwrite existing report files in the output path.",
        ),
    ] = False,
):
    if sde_directory.glob("*.jsonl"):
        report = get_jsonl_schema_report(sde_directory)
    elif sde_directory.glob("*.yaml"):
        report = get_yaml_schema_report(sde_directory)
    elif sde_directory.glob("*.json"):
        report = get_json_schema_report(sde_directory)
    else:
        raise ValueError("No supported data files found in the specified directory.")
    markdown_report = generate_markdown_report(report)
    if output_path:
        report_file = output_path / "schema_report.json"
        json_dumps_path(report, filepath=report_file, indent=2, overwrite=overwrite)
        markdown_report_file = output_path / "schema_report.md"
        save_text_file(
            markdown_report,
            output_path=output_path,
            file_name=markdown_report_file.name,
            overwrite=overwrite,
        )
    else:
        print(markdown_report)


if __name__ == "__main__":
    app()
