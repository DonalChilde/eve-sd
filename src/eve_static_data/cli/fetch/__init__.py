"""Commands for fetching SDE content."""

import typer

from eve_static_data.cli.fetch.download_sde import app as download_sde_app
from eve_static_data.cli.fetch.latest import app as latest_sde_app
from eve_static_data.cli.fetch.schema_changes import app as schema_changes_app
from eve_static_data.cli.fetch.sde_changes import app as data_changes_app

app = typer.Typer(no_args_is_help=True)

app.add_typer(download_sde_app)
app.add_typer(latest_sde_app)
app.add_typer(schema_changes_app)
app.add_typer(data_changes_app)
