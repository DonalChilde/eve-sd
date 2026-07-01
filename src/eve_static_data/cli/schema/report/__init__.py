import typer

from eve_static_data.cli.schema.report.db import app as report_db_app
from eve_static_data.cli.schema.report.files import app as report_files_app

app = typer.Typer(no_args_is_help=True)

app.add_typer(report_files_app)
app.add_typer(report_db_app)
