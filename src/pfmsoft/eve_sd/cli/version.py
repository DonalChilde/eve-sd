"""Display the installed eve-sd version and project URL."""

import typer

from pfmsoft.eve_sd import __app_name__, __url__, __version__

app = typer.Typer(no_args_is_help=True)

# TODO can useragent be a useful version string?


@app.command()
def version(ctx: typer.Context):
    """Print the current application version and project URL."""
    typer.echo(f"{__app_name__} v{__version__}")
    typer.echo(f"Project URL: {__url__}")
