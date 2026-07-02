"""Generate schema reports from an existing SDE SQLite database."""

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from eve_static_data.cli.helpers import ReportChoice
from eve_static_data.db.helpers import create_read_write_connection
from eve_static_data.helpers import json_io
from eve_static_data.helpers.save_text_file import save_text_file
from eve_static_data.helpers.schema_report.markdown_report import (
    generate_markdown_report,
)
from eve_static_data.helpers.schema_report.report_from_db import (
    get_schema_report_from_db,
)

app = typer.Typer(no_args_is_help=True)


@app.command(name="db")
def report_db(
    from_file: Annotated[
        Path,
        typer.Option(
            "--from",
            help="The path to the SQLite database file.",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
        ),
    ],
    to_directory: Annotated[
        Path | None,
        typer.Option(
            "--to",
            help="The directory to save the SDE schema report to.",
            file_okay=False,
            dir_okay=True,
        ),
    ] = None,
    update_db: Annotated[
        bool,
        typer.Option(
            "--update-db",
            help="Whether to update the database with the latest schema information.",
            show_default=True,
        ),
    ] = False,
    stdout_format: Annotated[
        ReportChoice,
        typer.Option(
            "--stdout-format",
            help="The format of the schema report to print to stdout.",
            case_sensitive=False,
            show_default=True,
        ),
    ] = ReportChoice.MARKDOWN,
    overwrite: Annotated[
        bool,
        typer.Option(
            "--overwrite",
            help="Overwrite existing report files when writing output.",
        ),
    ] = False,
    quiet: Annotated[
        bool,
        typer.Option(
            "--quiet",
            help="Suppress output messages.",
        ),
    ] = False,
) -> None:
    """Generate a schema report from a SQLite database."""
    if quiet:
        messenger = Console(stderr=True, quiet=True)
    else:
        messenger = Console(stderr=True)
    stdout = Console()
    connection = create_read_write_connection(str(from_file))
    try:
        # TODO Refactor to allow progress bar.
        schema_report = get_schema_report_from_db(connection)
    finally:
        connection.close()

    markdown_report = generate_markdown_report(schema_report)
    if update_db:
        raise NotImplementedError(
            "Updating the database with schema information is not yet implemented."
        )
    match stdout_format:
        case ReportChoice.JSON:
            stdout.print(json_io.json_dumps(schema_report, indent=2))
        case ReportChoice.MARKDOWN:
            stdout.print(markdown_report)
        case ReportChoice.NONE:
            pass
    if to_directory is None:
        return

    build_number = schema_report["sde_metadata"].buildNumber
    format_name = schema_report["sde_metadata"].variant
    json_file_name = f"schema_report_{format_name}_{build_number}.json"
    markdown_file_name = f"schema_report_{format_name}_{build_number}.md"
    save_text_file(
        text=json_io.json_dumps(schema_report, indent=2),
        output_directory=to_directory,
        file_name=json_file_name,
        overwrite=overwrite,
    )
    save_text_file(
        text=markdown_report,
        output_directory=to_directory,
        file_name=markdown_file_name,
        overwrite=overwrite,
    )
    messenger.print(
        f"[bold green]Schema report saved to {to_directory} as {json_file_name} and {markdown_file_name}[/bold green]"
    )
