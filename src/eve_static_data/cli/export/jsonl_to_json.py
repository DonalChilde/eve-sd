"""CLI command to convert SDE data from JSONL format to JSON format."""

import typer

app = typer.Typer(no_args_is_help=True)


@app.command()
def jsonl_to_json():
    """Convert SDE data from JSONL format to JSON format."""
    raise NotImplementedError("This command is not yet implemented.")
