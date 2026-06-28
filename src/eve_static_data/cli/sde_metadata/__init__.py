"""SDE metadata related CLI commands."""

import typer

from eve_static_data.cli.sde_metadata.latest import app as latest_app

# from eve_static_data.cli.sde_metadata.schema_report import app as schema_report_app

app = typer.Typer(
    no_args_is_help=True,
    name="sde-metadata",
    help="Commands for working with SDE metadata.",
)

app.add_typer(latest_app, help="Get the metadata for the latest SDE build.")
# app.add_typer(
#     schema_report_app, help="Generate a schema report from the SDE data files."
# )
