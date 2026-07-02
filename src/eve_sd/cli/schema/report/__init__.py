"""Schema report command group."""

import typer

from eve_sd.cli.schema.report.db import app as report_db_app
from eve_sd.cli.schema.report.files import app as report_files_app

app = typer.Typer(
    no_args_is_help=True,
    help="Generate schema reports from dataset files or from a local database.",
)

app.add_typer(
    report_files_app,
    help="Generate schema reports by reading local dataset files.",
)
app.add_typer(
    report_db_app,
    help="Generate schema reports by reading a local SQLite database.",
)
