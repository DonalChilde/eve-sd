import typer

from eve_static_data.cli.schema.export import app as export_app
from eve_static_data.cli.schema.report import app as report_app

app = typer.Typer(no_args_is_help=True)

app.add_typer(export_app, name="export", help="Commands for exporting schema data.")
app.add_typer(report_app, name="report", help="Commands for generating schema reports.")
