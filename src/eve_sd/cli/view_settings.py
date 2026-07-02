"""Display effective eve-sd runtime settings."""

import typer
from rich.console import Console
from rich.text import Text

from eve_sd import USER_AGENT
from eve_sd.cli.helpers import get_esd_settings_from_context

app = typer.Typer(no_args_is_help=True)


@app.command()
def settings(ctx: typer.Context):
    """Print effective settings and the current User-Agent string."""
    console = Console()
    console.rule(Text("Eve Static Data CLI Settings", style="bold cyan"))
    settings = get_esd_settings_from_context(ctx)
    console.print(settings)
    console.print(f"User Agent: {USER_AGENT}")
