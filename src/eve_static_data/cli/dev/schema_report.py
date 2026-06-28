"""Generate schema reports for local SDE datasets."""

from enum import Enum
from pathlib import Path
from typing import Annotated

import typer

from eve_static_data.helpers import json_io
from eve_static_data.helpers.save_text_file import save_text_file
from eve_static_data.helpers.schema_report.markdown_report import (
    generate_markdown_report,
)
from eve_static_data.helpers.schema_report.report_from_files import (
    get_json_schema_report,
    get_jsonl_schema_report,
    get_yaml_schema_report,
)

app = typer.Typer(no_args_is_help=True)


class DatasetFormat(str, Enum):
    """Supported dataset formats for schema report generation."""

    auto = "auto"
    yaml = "yaml"
    jsonl = "jsonl"
    json = "json"


def _has_files(sde_path: Path, suffix: str) -> bool:
    """Return whether the directory contains at least one file with suffix."""
    return next(sde_path.glob(f"*{suffix}"), None) is not None


def _resolve_format(sde_path: Path, dataset_format: DatasetFormat) -> DatasetFormat:
    """Resolve auto format selection based on files present in the directory."""
    if dataset_format is not DatasetFormat.auto:
        return dataset_format

    if _has_files(sde_path, ".yaml"):
        return DatasetFormat.yaml
    if _has_files(sde_path, ".jsonl"):
        return DatasetFormat.jsonl
    if _has_files(sde_path, ".json"):
        return DatasetFormat.json

    raise typer.BadParameter(
        "No supported dataset files found. Expected .yaml, .jsonl, or .json files."
    )


@app.command(name="files")
def report_files(
    sde_path: Annotated[
        Path,
        typer.Argument(
            help="Path to a directory containing SDE dataset files.",
            exists=True,
            file_okay=False,
            dir_okay=True,
            readable=True,
        ),
    ],
    dataset_format: Annotated[
        DatasetFormat,
        typer.Option(
            "--format",
            help="Dataset format in the directory. Defaults to auto detection.",
            case_sensitive=False,
        ),
    ] = DatasetFormat.auto,
    report_path: Annotated[
        Path | None,
        typer.Option(
            "--report-path",
            help=(
                "Directory to save the schema report JSON and markdown files. "
                "When omitted, the markdown report is printed to the terminal."
            ),
            file_okay=False,
            dir_okay=True,
        ),
    ] = None,
    overwrite: Annotated[
        bool,
        typer.Option(
            "--overwrite",
            help="Overwrite existing report files when writing output.",
        ),
    ] = False,
) -> None:
    """Generate a schema report from local datasets in one directory."""
    resolved_format = _resolve_format(sde_path, dataset_format)

    if resolved_format is DatasetFormat.yaml:
        schema_report = get_yaml_schema_report(sde_path)
    elif resolved_format is DatasetFormat.jsonl:
        schema_report = get_jsonl_schema_report(sde_path)
    else:
        schema_report = get_json_schema_report(sde_path)

    markdown_report = generate_markdown_report(schema_report)
    if report_path is None:
        typer.echo(markdown_report)
        return

    format_name = resolved_format.value
    json_file_name = f"schema_report_{format_name}.json"
    markdown_file_name = f"schema_report_{format_name}.md"
    save_text_file(
        text=json_io.json_dumps(schema_report, indent=2),
        output_dir=report_path,
        file_name=json_file_name,
        overwrite=overwrite,
    )
    save_text_file(
        text=markdown_report,
        output_dir=report_path,
        file_name=markdown_file_name,
        overwrite=overwrite,
    )
    typer.echo(f"Saved schema report files to {report_path}")
