"""CLI commands for development and maintenance workflows."""

import typer

from eve_static_data.cli.dev.db_perf import app as db_perf_app
from eve_static_data.cli.dev.generate_test_data import app as generate_test_data_app
from eve_static_data.cli.dev.rollup import app as rollup_app
from eve_static_data.cli.dev.schema_changes import app as schema_changes_app
from eve_static_data.cli.dev.schema_report import app as schema_report_app
from eve_static_data.cli.dev.sde_changes import app as data_changes_app

# from eve_static_data.cli.dev.sde_validate import app as validate_app

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
# app.add_typer(
#     validate_app,
#     name="validate",
#     help="Validate SDE datasets.",
# )
app.add_typer(
    schema_changes_app,
    name="schema-changes",
    help="Fetch SDE schema changelog content.",
)
app.add_typer(
    data_changes_app,
    name="data-changes",
    help="Fetch SDE data changelog content.",
)
app.add_typer(
    rollup_app,
    name="rollup",
    help="Run report, validation, and changelog collection as one workflow.",
)
app.add_typer(
    db_perf_app,
)
