"""Display bundled project documentation in the terminal or save it to disk."""

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from pfmsoft.eve_sd.docs import get_docs_text
from pfmsoft.eve_sd.helpers.save_text_file import save_text_file

app = typer.Typer(
    no_args_is_help=True,
    help="Display bundled documentation for eve-sd.",
)
_doc_parent = "eve_static_data.docs"
_doc_file = "eve_static_data_docs.md"


@app.command(name="docs")
def docs(
    ctx: typer.Context,
    to_directory: Annotated[
        Path,
        typer.Option(
            "--to",
            help="The directory to save the documentation file. Defaults to stdout.",
            file_okay=False,
            dir_okay=True,
            allow_dash=True,
            show_default=True,
        ),
    ] = Path("-"),
    overwrite: Annotated[
        bool,
        typer.Option(
            "--overwrite",
            help="Overwrite an existing documentation file when writing output.",
        ),
    ] = False,
    quiet: Annotated[
        bool,
        typer.Option(
            "--quiet",
            help="Suppress output messages.",
        ),
    ] = False,
):
    """Display bundled documentation for eve-sd."""
    if quiet:
        messenger = Console(stderr=True, quiet=True)
    else:
        messenger = Console(stderr=True)
    stdout = Console()
    doc_text = get_docs_text()
    if to_directory == Path("-"):
        stdout.print(doc_text)
    else:
        path_out = save_text_file(
            text=doc_text,
            output_directory=to_directory,
            file_name=_doc_file,
            overwrite=overwrite,
        )
        messenger.print(f"Documentation saved to: {path_out}")
