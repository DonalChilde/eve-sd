"""Commands to download SDE data in various formats."""

import json
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from eve_static_data.cli.helpers import get_esd_settings_from_context
from eve_static_data.helpers.http_client import config_http_client
from eve_static_data.helpers.sde_metadata import SdeVariant
from eve_static_data.helpers.settings_factory import sde_tools_factory

app = typer.Typer(no_args_is_help=True)


@app.command(name="sde")
def download_sde(
    ctx: typer.Context,
    to_directory: Annotated[
        Path,
        typer.Option(
            "--to",
            help="The directory to save the downloaded SDE data. The file name will "
            "be automatically generated.",
            file_okay=False,
        ),
    ],
    variant: Annotated[
        SdeVariant,
        typer.Option(
            "--variant",
            help="The variant of the SDE data to download.",
            show_default=True,
        ),
    ] = SdeVariant.YAML,
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
    quiet: Annotated[
        bool,
        typer.Option(
            "--quiet",
            help="Suppress output messages.",
        ),
    ] = False,
):
    """Download the latest SDE data in the specified format."""
    if quiet:
        messenger = Console(stderr=True, quiet=True)
    else:
        messenger = Console(stderr=True)

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
    messenger.print(
        f"Downloading SDE data, build number {build_number}, {variant.value.upper()} variant."
    )

    try:
        file_path = sde_tools.download(
            build_number=build_number,
            output_directory=to_directory,
            variant=variant.value,
            overwrite=overwrite,
            session=session,
        )

    except Exception as e:
        messenger.print(f"[bold red]Error:[/bold red] Failed to download SDE data: {e}")
        raise typer.Exit(code=1) from e

    messenger.print(f"SDE data downloaded successfully. Saved to: {file_path}")
