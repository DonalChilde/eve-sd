"""Command to display app version."""

import typer

from eve_static_data import AFTER_BUILD_NUMBER, RELEASE_DATE, __app_name__, __version__

app = typer.Typer(no_args_is_help=True)

# TODO can useragent be a useful version string?


@app.command()
def version(ctx: typer.Context):
    """Show the eve-static-data app version."""
    typer.echo(f"{__app_name__} v{__version__}")
