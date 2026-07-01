"""CLI commands for development and maintenance workflows."""

import typer

from eve_static_data.cli.dev.compare import app as compare_app
from eve_static_data.cli.dev.db_perf import app as db_perf_app
from eve_static_data.cli.dev.generate_test_data import app as generate_test_data_app

app = typer.Typer(no_args_is_help=True)


app.add_typer(
    generate_test_data_app,
    name="generate-test-data",
    help="Generate small fixture datasets from SDE files.",
)


app.add_typer(
    db_perf_app,
)
app.add_typer(
    compare_app,
)
