"""Schema export command group."""

import typer

app = typer.Typer(
    no_args_is_help=True,
    help="Export schema information to files or other formats.",
)
