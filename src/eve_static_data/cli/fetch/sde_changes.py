"""Command to fetch and show the data changes for an SDE build number."""

import json
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from eve_static_data.cli.helpers import get_esd_settings_from_context
from eve_static_data.helpers.http_client import config_http_client
from eve_static_data.helpers.save_text_file import save_text_file
from eve_static_data.helpers.settings_factory import sde_tools_factory

app = typer.Typer(no_args_is_help=True)


@app.command()
def data_changes(
    ctx: typer.Context,
    to_directory: Annotated[
        Path,
        typer.Option(
            "--to",
            help="The path to save the SDE data changelog information as a jsonl file. Defaults to stdout.",
            file_okay=False,
            dir_okay=True,
            allow_dash=True,
            show_default=True,
        ),
    ] = Path("-"),
    build_number: Annotated[
        int | None,
        typer.Option(
            help="The SDE build number to show the data changes for. If not "
            "provided, the changes for the latest build will be shown.",
            show_default=True,
        ),
    ] = None,
    file_name: Annotated[
        Path | None,
        typer.Option(
            "--file-name",
            help="The file name for the SDE data changelog. If not provided, the file "
            "name will be `sde_data_changelog_<build_number>.jsonl`.",
            file_okay=True,
            show_default=True,
        ),
    ] = None,
    overwrite: Annotated[
        bool,
        typer.Option(
            "--overwrite",
            help="Overwrite existing changes file when writing output.",
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
    """Fetch and show the data changes for an SDE build number.

    Note the changes for the SDE data is different from the changes for the SDE schema.
    The SDE data changelog tracks changes in the actual data, while the SDE schema changelog
    tracks changes in the structure of the data.

    The data changes are in JSONL format, where each line is a JSON object representing
    a change in the SDE data.
    """
    if quiet:
        messenger = Console(stderr=True, quiet=True)
    else:
        messenger = Console(stderr=True)
    stdout = Console()

    messenger.print("[bold green]Fetching SDE Data Changelog[/bold green]")

    settings = get_esd_settings_from_context(ctx)
    session = config_http_client()
    sde_tools = sde_tools_factory(settings)
    if build_number is None:
        messenger.print("No build number provided, resolving latest build number...")
        latest_info = sde_tools.fetch_latest_sde_info(session=session)
        latest_info = json.loads(latest_info)
        build_number = latest_info.get("buildNumber")
        if not build_number:
            messenger.print(
                "[bold red]Error:[/bold red] Could not resolve latest build number."
            )
            messenger.print(latest_info)
            raise typer.Exit(code=1)
        messenger.print(f"Resolved latest build number to: {build_number}")
    changelog = sde_tools.fetch_data_changes(build_number=build_number, session=session)
    if str(to_directory) == "-":
        messenger.print(
            f"[bold green]SDE Data Changelog for build {build_number}:[/bold green]"
        )
        stdout.print(changelog)
        return
    if file_name is None:
        file_name = Path(f"sde_data_changelog_{build_number}.jsonl")

    path_out = save_text_file(
        text=changelog,
        output_directory=to_directory,
        file_name=str(file_name),
        overwrite=overwrite,
    )
    messenger.print(
        f"[bold green]SDE Data Changelog for build {build_number} saved to {path_out}[/bold green]"
    )
