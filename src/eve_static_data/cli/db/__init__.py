import typer

from eve_static_data.cli.db.from_jsonl import app as from_jsonl_app
from eve_static_data.cli.db.from_yaml import app as from_yaml_app

app = typer.Typer(
    no_args_is_help=True, name="db", help="Commands for working with the SDE database."
)

app.add_typer(from_yaml_app, help="Import SDE data from YAML files into the database.")
app.add_typer(
    from_jsonl_app, help="Import SDE data from JSONL files into the database."
)
