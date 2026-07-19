"""Unpack downloaded SDE archives into local directories."""

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from pfmsoft.eve_sd.cli.helpers import get_esd_settings_from_context
from pfmsoft.eve_sd.helpers.settings_factory import sde_tools_factory

app = typer.Typer(no_args_is_help=True)


@app.command()
def unpack(
    ctx: typer.Context,
    from_file: Annotated[
        Path,
        typer.Option(
            "--from",
            help="The path to the SDE data zip file.",
            exists=True,
            file_okay=True,
            dir_okay=False,
        ),
    ],
    to_directory: Annotated[
        Path,
        typer.Option(
            "--to",
            help="The directory to save the extracted SDE data to.",
            file_okay=False,
            dir_okay=True,
        ),
    ],
    build_number: Annotated[
        bool,
        typer.Option(
            help="Whether to use the build number in the output directory structure. "
            "If True, the extracted data will be saved to `<output_path>/<build_number>/`. "
            "If False, the extracted data will be saved directly to `<output_path>/`.",
            show_default=True,
        ),
    ] = True,
    quiet: Annotated[
        bool,
        typer.Option(
            "--quiet",
            help="Suppress output messages.",
            show_default=True,
        ),
    ] = False,
):
    """Unpack downloaded SDE archives into local dataset directories."""
    if quiet:
        messenger = Console(stderr=True, quiet=True)
    else:
        messenger = Console(stderr=True)
    messenger.print("[bold green]Extracting SDE Data[/bold green]")
    settings = get_esd_settings_from_context(ctx)
    sde_tools = sde_tools_factory(settings)
    # TODO refactor this to unhide the workings.
    # functions in an unpack helper module that can be tested and used in other contexts.
    # get sde metadata from zip.
    # manipulate the output path as desired.
    # unpack the zip to the output path.
    try:
        sde_path, sde_info = sde_tools.unpack(
            from_file, to_directory, use_build_number=build_number
        )
    except Exception as e:
        messenger.print(f"[bold red]Error:[/bold red] Failed to extract SDE data: {e}")
        raise typer.Exit(code=1) from e
    messenger.print(
        f"Extracted SDE {sde_info.buildNumber} - {sde_info.releaseDate} to {sde_path}"
    )
