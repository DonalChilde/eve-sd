import typer

from eve_static_data.cli.db.create import app as create_app

app = typer.Typer(
    no_args_is_help=True, name="db", help="Commands for working with the SDE database."
)

app.add_typer(create_app, help="Create a new SDE database.")
