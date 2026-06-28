"""Main CLI Typer app for esi-link."""

import logging
from pathlib import Path

import typer

from eve_static_data import __app_name__, __version__
from eve_static_data.cli.config_info import app as config_info_app
from eve_static_data.cli.db import app as sde_import_app
from eve_static_data.cli.dev import app as dev_app
from eve_static_data.cli.export import app as sde_export_app
from eve_static_data.cli.sde_metadata.latest import app as sde_latest_app
from eve_static_data.cli.sde_zip import app as sde_zip_app
from eve_static_data.logging_config import setup_logging
from eve_static_data.settings import get_settings

logger = logging.getLogger(__name__)

app = typer.Typer(no_args_is_help=True)
app.add_typer(
    sde_import_app, name="db", help="Commands for working with the SDE database."
)
app.add_typer(
    sde_latest_app,
)
app.add_typer(sde_zip_app, name="zip", help="Commands for working with SDE zip files.")
app.add_typer(sde_export_app, name="export", help="Commands for exporting SDE data.")
app.add_typer(dev_app, name="dev", help="Commands for development workflows.")
# app.add_typer(sde_import_app, name="import", help="Commands for importing SDE data.")
app.add_typer(
    config_info_app,
    name="self",
    help="Commands for displaying configuration information about the current environment.",
)


@app.callback(invoke_without_command=True)
def default_options(
    ctx: typer.Context,
):
    """Esi Link Command Line Interface.

    This CLI provides various commands for working with eve-static-data, including
    network operations, development tools, and import/export functionality.
    """
    settings = get_settings()
    setup_logging(log_dir=Path(settings.logging_directory))
    logger.info(f"Starting {__app_name__} v{__version__}")
    ctx.obj = {"esd-settings": settings}
