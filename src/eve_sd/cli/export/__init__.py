"""CLI commands for exporting SDE data."""

import typer

from eve_sd.cli.export.jsonl_to_json import app as jsonl_to_json_app
from eve_sd.cli.export.yaml_to_json import app as yaml_to_json_app

app = typer.Typer(
    no_args_is_help=True,
    help="Convert SDE datasets between supported file formats.",
)

app.add_typer(
    yaml_to_json_app,
    help="Convert SDE data from YAML format to JSON format.",
)
app.add_typer(
    jsonl_to_json_app,
    help="Convert SDE data from JSONL format to JSON format.",
)
