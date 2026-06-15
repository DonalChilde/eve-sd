"""Commands to download SDE data in various formats."""

import json
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from eve_static_data.cli.helpers import get_esd_settings_from_context
from eve_static_data.helpers.http_client import config_http_client
from eve_static_data.helpers.settings_factory import sde_tools_factory

app = typer.Typer(no_args_is_help=True)


@app.command(name="download-yaml")
def download_yaml(
    ctx: typer.Context,
    output_dir: Annotated[
        Path,
        typer.Argument(
            help="The directory to save the downloaded SDE data. The file name will "
            "be automatically generated.",
            file_okay=False,
        ),
    ],
    build_number: Annotated[
        int | None,
        typer.Option(
            "--build-number",
            help="The build number of the SDE to download. If not provided, the latest "
            "build will be downloaded.",
            show_default=True,
        ),
    ] = None,  # None will be resolved to latest build number
    overwrite: Annotated[
        bool,
        typer.Option(
            "--overwrite", help="Whether to overwrite existing files", show_default=True
        ),
    ] = False,
):
    """Download the latest SDE data in YAML format."""
    console = Console()
    error_console = Console(stderr=True)
    console.print("[bold green]Downloading YAML SDE Data...[/bold green]")
    settings = get_esd_settings_from_context(ctx)
    session = config_http_client()
    sde_tools = sde_tools_factory(settings)
    if build_number is None:
        console.print("No build number provided, resolving latest build number...")
        latest_info = sde_tools.fetch_latest_sde_info(session=session)
        latest_info = json.loads(latest_info)
        build_number = latest_info.get("buildNumber")
        release_date = latest_info.get("releaseDate")
        if not build_number:
            error_console.print(
                "[bold red]Error:[/bold red] Could not resolve latest build number."
            )
            error_console.print(latest_info)
            raise typer.Exit(code=1)
        console.print(
            f"Resolved latest build number to: {build_number}, released on {release_date}"
        )

    console.print(f"Downloading SDE data, YAML variant.")

    try:
        file_path = sde_tools.download(
            build_number=build_number,
            output_directory=output_dir,
            variant="yaml",
            overwrite=overwrite,
            session=session,
        )

    except Exception as e:
        error_console.print(
            f"[bold red]Error:[/bold red] Failed to download SDE data: {e}"
        )
        raise typer.Exit(code=1) from e

    console.print(
        f"SDE data, YAML variant, downloaded successfully. Saved to: {file_path}"
    )


@app.command(name="download-jsonl")
def download_jsonl(
    ctx: typer.Context,
    output_dir: Annotated[
        Path,
        typer.Argument(
            help="The directory to save the downloaded SDE data. The file name will "
            "be automatically generated.",
            file_okay=False,
        ),
    ],
    build_number: Annotated[
        int | None,
        typer.Option(
            "--build-number",
            help="The build number of the SDE to download. If not provided, the latest "
            "build will be downloaded.",
            show_default=True,
        ),
    ] = None,  # None will be resolved to latest build number
    overwrite: Annotated[
        bool,
        typer.Option(
            "--overwrite", help="Whether to overwrite existing files", show_default=True
        ),
    ] = False,
):
    """Download the latest SDE data in jsonl format."""
    console = Console()
    error_console = Console(stderr=True)
    console.print("[bold green]Downloading JSONL SDE Data...[/bold green]")
    settings = get_esd_settings_from_context(ctx)
    session = config_http_client()
    sde_tools = sde_tools_factory(settings)
    if build_number is None:
        console.print("No build number provided, resolving latest build number...")
        latest_info = sde_tools.fetch_latest_sde_info(session=session)
        latest_info = json.loads(latest_info)
        build_number = latest_info.get("buildNumber")
        release_date = latest_info.get("releaseDate")
        if not build_number:
            error_console.print(
                "[bold red]Error:[/bold red] Could not resolve latest build number."
            )
            error_console.print(latest_info)
            raise typer.Exit(code=1)
        console.print(
            f"Resolved latest build number to: {build_number}, released on {release_date}"
        )

    console.print(f"Downloading SDE data, JSONL variant.")

    try:
        file_path = sde_tools.download(
            build_number=build_number,
            output_directory=output_dir,
            variant="jsonl",
            overwrite=overwrite,
            session=session,
        )

    except Exception as e:
        error_console.print(
            f"[bold red]Error:[/bold red] Failed to download SDE data: {e}"
        )
        raise typer.Exit(code=1) from e

    console.print(
        f"SDE data, JSONL variant, downloaded successfully. Saved to: {file_path}"
    )
