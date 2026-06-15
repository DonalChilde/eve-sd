"""Commands to extract SDE data from a zip file."""

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from eve_static_data.cli.helpers import get_esd_settings_from_context
from eve_static_data.helpers.settings_factory import sde_tools_factory

app = typer.Typer(no_args_is_help=True)


@app.command()
def extract(
    ctx: typer.Context,
    sde_zip: Annotated[
        Path,
        typer.Argument(
            help="The path to the SDE data zip file.",
            exists=True,
            file_okay=True,
            dir_okay=False,
        ),
    ],
    output_path: Annotated[
        Path,
        typer.Argument(
            help="The directory to save the extracted SDE data to.",
            file_okay=False,
            dir_okay=True,
        ),
    ],
    use_build_number: Annotated[
        bool,
        typer.Option(
            "-b",
            "--use-build-number",
            help="Whether to use the build number in the output directory structure. "
            "If True, the extracted data will be saved to `<output_path>/<build_number>/`. "
            "If False, the extracted data will be saved directly to `<output_path>/`.",
            show_default=True,
        ),
    ] = True,
):
    """Extract the SDE data from a zip file."""
    console = Console()
    console.print("[bold green]Extracting SDE Data[/bold green]")
    settings = get_esd_settings_from_context(ctx)
    sde_tools = sde_tools_factory(settings)
    try:
        sde_path, sde_info = sde_tools.unpack(
            sde_zip, output_path, use_build_number=use_build_number
        )
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] Failed to extract SDE data: {e}")
        raise typer.Exit(code=1) from e
    console.print(
        f"Extracted SDE {sde_info.buildNumber} - {sde_info.releaseDate} to {sde_path}"
    )
