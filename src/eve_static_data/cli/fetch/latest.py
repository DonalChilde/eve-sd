"""Command to fetch and show information about the latest available SDE data."""

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from eve_static_data.cli.helpers import get_esd_settings_from_context
from eve_static_data.helpers.http_client import config_http_client
from eve_static_data.helpers.settings_factory import sde_tools_factory

app = typer.Typer(no_args_is_help=True)


@app.command()
def latest(
    ctx: typer.Context,
    file_out: Annotated[
        Path | None,
        typer.Option(
            "--file-out",
            help="The file to save the latest SDE information to a json file.",
            file_okay=True,
        ),
    ] = None,
    pipe: Annotated[
        bool,
        typer.Option(
            "--pipe",
            help="Whether to print the latest SDE information to stdout.",
            show_default=True,
        ),
    ] = False,
):
    """Fetch and show information about the latest available SDE data."""
    console = Console()
    error_console = Console(stderr=True)
    if not file_out and not pipe:
        error_console.print(
            "[bold red]Error:[/bold red] No output method specified. Please provide a file path or enable terminal output."
        )
        raise typer.Exit(code=1)
    if not pipe:
        console.print("[bold green]Latest SDE Information[/bold green]")
    settings = get_esd_settings_from_context(ctx)
    sde_tools = sde_tools_factory(settings)
    session = config_http_client()
    info = sde_tools.fetch_latest_sde_info(session=session)
    if pipe:
        console.print(info)
    if file_out:
        try:
            with file_out.open("w", encoding="utf-8") as f:
                f.write(str(info))
            if not pipe:
                console.print(f"Latest SDE information saved to {file_out}")
        except Exception as e:
            error_console.print(
                f"[bold red]Error:[/bold red] Failed to save latest SDE information to file: {e}"
            )
            raise typer.Exit(code=1) from e
