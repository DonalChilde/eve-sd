"""Entrypoint for the eve-sd command-line interface."""

import logging
from pathlib import Path

import typer

from pfmsoft.eve_sd import __app_name__, __version__
from pfmsoft.eve_sd.cli.db import app as sde_import_app
from pfmsoft.eve_sd.cli.dev import app as dev_app
from pfmsoft.eve_sd.cli.docs import app as docs_app
from pfmsoft.eve_sd.cli.export import app as sde_export_app
from pfmsoft.eve_sd.cli.fetch import app as fetch_app
from pfmsoft.eve_sd.cli.schema import app as schema_app
from pfmsoft.eve_sd.cli.unpack_sde import app as unpack_app
from pfmsoft.eve_sd.cli.version import app as version_app
from pfmsoft.eve_sd.cli.view_settings import app as view_settings_app
from pfmsoft.eve_sd.logging_config import setup_logging
from pfmsoft.eve_sd.settings import get_settings

logger = logging.getLogger(__name__)

app = typer.Typer(
    no_args_is_help=True,
    help=(
        "Work with EVE Online static data: fetch releases, unpack datasets, "
        "build/query databases, export formats, and inspect schemas."
    ),
)

app.add_typer(fetch_app, name="fetch")
app.add_typer(unpack_app)
app.add_typer(sde_import_app, name="db")
app.add_typer(sde_export_app, name="export")
# app.add_typer(sde_import_app, name="import", help="Commands for importing SDE data.")

app.add_typer(schema_app, name="schema")
app.add_typer(dev_app, name="dev")

app.add_typer(version_app)
app.add_typer(view_settings_app)
app.add_typer(docs_app)


@app.callback(invoke_without_command=True)
def default_options(
    ctx: typer.Context,
):
    """Initialize shared CLI context before subcommands run.

    This callback configures application logging and stores loaded settings in
    the Typer context object so subcommands can reuse them.

    Args:
        ctx: Typer context used to share state between commands.
    """
    settings = get_settings()
    setup_logging(log_dir=Path(settings.logging_directory))
    logger.info(f"Starting {__app_name__} v{__version__}")
    ctx.obj = {"esd-settings": settings}
