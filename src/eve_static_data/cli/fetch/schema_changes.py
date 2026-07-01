"""Command to fetch and show the schema changes for an SDE build number."""

import json
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from eve_static_data.cli.helpers import get_esd_settings_from_context
from eve_static_data.helpers.http_client import config_http_client
from eve_static_data.helpers.settings_factory import sde_tools_factory

app = typer.Typer(no_args_is_help=True)


@app.command()
def schema_changes(
    ctx: typer.Context,
    build_number: Annotated[
        int | None,
        typer.Option(
            help="The build number of the SDE schema changelog to fetch. If not provided, "
            "the changelog for the latest build will be fetched.",
        ),
    ] = None,
    file_out: Annotated[
        Path | None,
        typer.Option(
            "--file-out",
            help="The file to save the SDE schema changelog information to a yaml file.",
            file_okay=True,
        ),
    ] = None,
    pipe: Annotated[
        bool,
        typer.Option(
            "--pipe",
            help="Whether to print the SDE schema changelog information to stdout.",
            show_default=True,
        ),
    ] = False,
):
    """Fetch and show the changelog for the SDE schema."""
    console = Console()
    error_console = Console(stderr=True)
    if not file_out and not pipe:
        error_console.print(
            "[bold red]Error:[/bold red] No output method specified. Please provide a file path or enable terminal output."
        )
        raise typer.Exit(code=1)
    if not pipe:
        console.print("[bold green]SDE Schema Changelog[/bold green]")
    settings = get_esd_settings_from_context(ctx)
    session = config_http_client()
    sde_tools = sde_tools_factory(settings)
    if build_number is None:
        if not pipe:
            console.print("No build number provided, resolving latest build number...")
        latest_info = sde_tools.fetch_latest_sde_info(session=session)
        latest_info = json.loads(latest_info)
        build_number = latest_info.get("buildNumber")
        if not build_number:
            error_console.print(
                "[bold red]Error:[/bold red] Could not resolve latest build number."
            )
            error_console.print("Latest SDE information:")
            error_console.print(latest_info)
            raise typer.Exit(code=1)
        if not pipe:
            console.print(f"Resolved latest build number to: {build_number}")
    changelog = sde_tools.fetch_schema_changelog(
        build_number=build_number, session=session
    )
    if pipe:
        console.print(changelog)
    if file_out:
        try:
            with file_out.open("w", encoding="utf-8") as f:
                f.write(changelog)
            if not pipe:
                console.print(f"SDE schema changelog saved to {file_out}")
        except Exception as e:
            error_console.print(
                f"[bold red]Error:[/bold red] Failed to save SDE schema changelog to file: {e}"
            )
            raise typer.Exit(code=1) from e
