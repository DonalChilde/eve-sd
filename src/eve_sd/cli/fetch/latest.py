"""Fetch metadata for the latest available SDE release."""

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from eve_sd.cli.helpers import get_esd_settings_from_context
from eve_sd.helpers.http_client import config_http_client
from eve_sd.helpers.save_text_file import save_text_file
from eve_sd.helpers.settings_factory import sde_tools_factory

app = typer.Typer(no_args_is_help=True)


@app.command()
def latest(
    ctx: typer.Context,
    to_file: Annotated[
        Path,
        typer.Option(
            "--to",
            help="The path to save the latest SDE information as a json file. Defaults to stdout.",
            file_okay=False,
            dir_okay=True,
            allow_dash=True,
            show_default=True,
        ),
    ] = Path("-"),
    file_name: Annotated[
        Path | None,
        typer.Option(
            "--file-name",
            help="The file name for the latest SDE information. If not provided, the file name will be `latest_sde_info.json`.",
            file_okay=True,
        ),
    ] = None,
    overwrite: Annotated[
        bool,
        typer.Option(
            "--overwrite",
            help="Overwrite an existing output file when writing to disk.",
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
    """Fetch metadata for the latest available SDE release."""
    if quiet:
        messenger = Console(stderr=True, quiet=True)
    else:
        messenger = Console(stderr=True)
    stdout = Console()
    messenger.print("[bold green]Latest SDE Information[/bold green]")
    settings = get_esd_settings_from_context(ctx)
    sde_tools = sde_tools_factory(settings)
    session = config_http_client()
    info = sde_tools.fetch_latest_sde_info(session=session)
    if str(to_file) == "-":
        stdout.print(info)
        return
    if file_name is None:
        file_name = Path("latest_sde_info.json")
    path_out = save_text_file(
        text=str(info),
        output_directory=to_file,
        file_name=str(file_name),
        overwrite=overwrite,
    )
    messenger.print(
        f"[bold green]Latest SDE information saved to {path_out}[/bold green]"
    )
