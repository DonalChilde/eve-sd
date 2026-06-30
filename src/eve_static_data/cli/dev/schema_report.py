"""Generate schema reports for local SDE datasets."""

from pathlib import Path
from typing import Annotated

import typer

from eve_static_data.db.helpers import create_read_write_connection
from eve_static_data.helpers import json_io
from eve_static_data.helpers.save_text_file import save_text_file
from eve_static_data.helpers.schema_report.markdown_report import (
    generate_markdown_report,
)
from eve_static_data.helpers.schema_report.report_from_db import (
    get_schema_report_from_db,
)
from eve_static_data.helpers.schema_report.report_from_files import (
    get_json_schema_report,
    get_jsonl_schema_report,
    get_yaml_schema_report,
)
from eve_static_data.helpers.sde_metadata import (
    SourceMedia,
    load_sde_metadata,
)

app = typer.Typer(no_args_is_help=True)


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
    try:
        sde_metadata = load_sde_metadata(sde_path)
    except (FileNotFoundError, ValueError) as exc:
        raise typer.BadParameter(str(exc)) from exc

    if sde_metadata.source_media is SourceMedia.YAML:
        schema_report = get_yaml_schema_report(sde_path)
    elif sde_metadata.source_media is SourceMedia.JSONL:
        schema_report = get_jsonl_schema_report(sde_path)
    elif sde_metadata.source_media is SourceMedia.JSON:
        schema_report = get_json_schema_report(sde_path)
    else:
        raise typer.BadParameter(
            f"Unsupported source media {sde_metadata.source_media!r} for schema reporting."
        )

    markdown_report = generate_markdown_report(schema_report)
    if report_path is None:
        typer.echo(markdown_report)
        return

    build_suffix = sde_metadata.buildNumber
    format_name = sde_metadata.source_format.value
    json_file_name = f"schema_report_{format_name}_{build_suffix}.json"
    markdown_file_name = f"schema_report_{format_name}_{build_suffix}.md"
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


@app.command(name="db")
def report_db(
    db_path: Annotated[
        Path,
        typer.Argument(
            help="Path to the SQLite database file.",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
        ),
    ],
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
    """Generate a schema report from a SQLite database."""
    connection = create_read_write_connection(str(db_path))
    try:
        schema_report = get_schema_report_from_db(connection)
    finally:
        connection.close()

    markdown_report = generate_markdown_report(schema_report)
    if report_path is None:
        typer.echo(markdown_report)
        return

    build_suffix = schema_report["sde_metadata"].buildNumber
    format_name = schema_report["sde_metadata"].source_format
    json_file_name = f"schema_report_{format_name}_{build_suffix}.json"
    markdown_file_name = f"schema_report_{format_name}_{build_suffix}.md"
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
