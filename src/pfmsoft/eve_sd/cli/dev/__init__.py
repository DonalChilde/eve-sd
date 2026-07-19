"""CLI commands for development and maintenance workflows."""

import typer

from pfmsoft.eve_sd.cli.dev.compare import app as compare_app
from pfmsoft.eve_sd.cli.dev.db_perf import app as db_perf_app
from pfmsoft.eve_sd.cli.dev.generate_test_data import app as generate_test_data_app

app = typer.Typer(
    no_args_is_help=True,
    help="Developer-focused utilities for validation, comparison, and test data prep.",
)


app.add_typer(
    generate_test_data_app,
    name="generate-test-data",
    help="Generate small fixture datasets from SDE files.",
)


app.add_typer(
    db_perf_app,
    help="Run ad-hoc database performance checks against an SDE database.",
)
app.add_typer(
    compare_app,
    help="Compare records between source datasets and a local SDE database.",
)
