"""CLI commands for development and maintenance workflows."""

import typer

from eve_static_data.cli.dev.generate_test_data import app as generate_test_data_app
from eve_static_data.cli.dev.schema_report import app as schema_report_app

app = typer.Typer(no_args_is_help=True)

app.add_typer(
    schema_report_app,
    name="schema-report",
    help="Generate schema reports from local dataset files.",
)
app.add_typer(
    generate_test_data_app,
    name="generate-test-data",
    help="Generate small fixture datasets from SDE files.",
)
