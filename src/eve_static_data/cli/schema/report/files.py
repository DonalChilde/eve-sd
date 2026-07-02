"""Generate schema reports for local SDE datasets."""

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from eve_static_data.cli.helpers import ReportChoice
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
from eve_static_data.helpers.sde_metadata import (
    SourceMedia,
    load_sde_metadata,
)

app = typer.Typer(no_args_is_help=True)


@app.command(name="files")
def report_files(
    from_directory: Annotated[
        Path,
        typer.Option(
            "--from",
            help="The path to the directory containing the SDE dataset files.",
            exists=True,
            file_okay=False,
            dir_okay=True,
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
    """Generate a schema report from local datasets in one directory."""
    if quiet:
        messenger = Console(stderr=True, quiet=True)
    else:
        messenger = Console(stderr=True)
    stdout = Console()
    try:
        sde_metadata = load_sde_metadata(from_directory)
    except (FileNotFoundError, ValueError) as exc:
        raise typer.BadParameter(str(exc)) from exc
    messenger.print(
        f"[bold green]Generating schema report for SDE datasets in {from_directory}[/bold green]"
    )
    messenger.print(f"[bold green]SDE Metadata: {sde_metadata}[/bold green]")

    # TODO refactor to allow progress reporting.

    if sde_metadata.source_media is SourceMedia.YAML:
        schema_report = get_yaml_schema_report(from_directory)
    elif sde_metadata.source_media is SourceMedia.JSONL:
        schema_report = get_jsonl_schema_report(from_directory)
    elif sde_metadata.source_media is SourceMedia.JSON:
        schema_report = get_json_schema_report(from_directory)
    else:
        raise typer.BadParameter(
            f"Unsupported source media {sde_metadata.source_media!r} for schema reporting."
        )
    markdown_report = generate_markdown_report(schema_report)
    match stdout_format:
        case ReportChoice.JSON:
            stdout.print(json_io.json_dumps(schema_report, indent=2))
        case ReportChoice.MARKDOWN:
            stdout.print(markdown_report)
        case ReportChoice.NONE:
            pass
    if to_directory is None:
        return

    build_number = sde_metadata.buildNumber
    format_name = sde_metadata.variant.value
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
