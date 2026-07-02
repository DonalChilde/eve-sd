"""Commands for fetching SDE content."""

import typer

from eve_sd.cli.fetch.download_sde import app as download_sde_app
from eve_sd.cli.fetch.latest import app as latest_sde_app
from eve_sd.cli.fetch.schema_changes import app as schema_changes_app
from eve_sd.cli.fetch.sde_changes import app as data_changes_app

app = typer.Typer(
    no_args_is_help=True,
    help="Fetch SDE metadata, changelogs, and downloadable archives from Fenris Creations.",
)

app.add_typer(download_sde_app)
app.add_typer(latest_sde_app)
app.add_typer(schema_changes_app)
app.add_typer(data_changes_app)
