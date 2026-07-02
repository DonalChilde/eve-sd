"""Main CLI Typer app for esi-link."""

import logging
from pathlib import Path

import typer

from eve_static_data import __app_name__, __version__
from eve_static_data.cli.db import app as sde_import_app
from eve_static_data.cli.dev import app as dev_app
from eve_static_data.cli.docs import app as docs_app
from eve_static_data.cli.export import app as sde_export_app
from eve_static_data.cli.fetch import app as fetch_app
from eve_static_data.cli.schema import app as schema_app
from eve_static_data.cli.unpack_sde import app as unpack_app
from eve_static_data.cli.version import app as version_app
from eve_static_data.cli.view_settings import app as view_settings_app
from eve_static_data.logging_config import setup_logging
from eve_static_data.settings import get_settings

logger = logging.getLogger(__name__)

app = typer.Typer(no_args_is_help=True)

app.add_typer(
    fetch_app, name="fetch", help="Commands for fetching SDE changelog content."
)
app.add_typer(unpack_app)
app.add_typer(
    sde_import_app, name="db", help="Commands for working with the SDE database."
)
app.add_typer(sde_export_app, name="export", help="Commands for exporting SDE data.")
# app.add_typer(sde_import_app, name="import", help="Commands for importing SDE data.")

app.add_typer(
    schema_app,
    name="schema",
    help="Commands for working with schema data, including export and report generation.",
)
app.add_typer(dev_app, name="dev", help="Commands for development workflows.")

app.add_typer(
    version_app,
)
app.add_typer(view_settings_app)
app.add_typer(docs_app)


@app.callback(invoke_without_command=True)
def default_options(
    ctx: typer.Context,
):
    """EVE Static Data Command Line Interface.

    This CLI provides various commands for working with eve-static-data, including
    network operations, development tools, and import/export functionality.
    """
    settings = get_settings()
    setup_logging(log_dir=Path(settings.logging_directory))
    logger.info(f"Starting {__app_name__} v{__version__}")
    ctx.obj = {"esd-settings": settings}
