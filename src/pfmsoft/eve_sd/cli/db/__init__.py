"""Database-related CLI command group."""

import typer

from pfmsoft.eve_sd.cli.db.browse import app as browse_app
from pfmsoft.eve_sd.cli.db.create import app as create_app

app = typer.Typer(
    no_args_is_help=True,
    name="db",
    help="Create and browse local SQLite databases built from SDE datasets.",
)

app.add_typer(create_app, help="Create a new SDE database.")
app.add_typer(browse_app, help="Browse records in an SDE database.")
