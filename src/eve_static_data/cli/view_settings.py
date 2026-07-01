"""Command to display app settings."""

import typer
from rich.console import Console
from rich.text import Text

from eve_static_data import USER_AGENT
from eve_static_data.cli.helpers import get_esd_settings_from_context

app = typer.Typer(no_args_is_help=True)


@app.command()
def settings(ctx: typer.Context):
    """Show the eve-static-data app settings."""
    console = Console()
    console.rule(Text("Eve Static Data CLI Settings", style="bold cyan"))
    settings = get_esd_settings_from_context(ctx)
    console.print(settings)
    console.print(f"User Agent: {USER_AGENT}")
