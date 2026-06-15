"""Commands for working with SDE zip files."""

import typer

from eve_static_data.cli.sde_zip.download_sde import app as download_sde_app
from eve_static_data.cli.sde_zip.unpack_sde import app as unpack_sde_app

app = typer.Typer(
    no_args_is_help=True,
    name="sde-zip",
    help="Commands for working with SDE zip files.",
)

app.add_typer(download_sde_app, help="Commands to download SDE data.")
app.add_typer(unpack_sde_app, help="Commands to extract SDE data from a zip file.")
