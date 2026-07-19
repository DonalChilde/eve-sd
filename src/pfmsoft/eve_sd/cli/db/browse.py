"""Browse records in the SDE database."""

import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Annotated, Any

import typer
from pfmsoft.eve_snippets import yaml_io
from rich.console import Console

from pfmsoft.eve_sd.db.helpers import db_connection_manager
from pfmsoft.eve_sd.db.query import DatasetDbQuery

app = typer.Typer(no_args_is_help=True, help="Browse records in an SDE database.")


def _page_slice(items: Sequence[Any], *, page: int, page_size: int) -> list[Any]:
    """Return a 1-based page slice from a list of items."""
    start = (page - 1) * page_size
    end = start + page_size
    return list(items[start:end])


def _page_mapping_from_records(
    records: Sequence[tuple[str | int, dict[str | int, Any]]],
) -> dict[str | int, dict[str | int, Any]]:
    """Convert record tuples into a mapping suitable for YAML output."""
    return {record_key: record for record_key, record in records}


def _fetch_page_records(
    db_query: DatasetDbQuery,
    *,
    dataset_name: str,
    key_type: str,
    page: int,
    page_size: int,
    record_keys: list[str] | None = None,
) -> list[tuple[str | int, dict[str | int, Any]]]:
    """Fetch a single page of records for a dataset."""
    if record_keys:
        parsed_record_keys = _parse_record_keys(key_type, record_keys)
        page_record_keys = _page_slice(
            parsed_record_keys, page=page, page_size=page_size
        )
        if key_type == "int":
            fetched_records = list(
                db_query.get_int_records(
                    dataset_name, record_keys=set(page_record_keys)
                )
            )
        else:
            fetched_records = list(
                db_query.get_str_records(
                    dataset_name, record_keys=set(page_record_keys)
                )
            )
        records_by_key = {record_key: record for record_key, record in fetched_records}
        return [
            (record_key, records_by_key[record_key])
            for record_key in page_record_keys
            if record_key in records_by_key
        ]

    offset = (page - 1) * page_size
    if key_type == "int":
        return list(
            db_query.get_int_records_page(dataset_name, limit=page_size, offset=offset)
        )
    return list(
        db_query.get_str_records_page(dataset_name, limit=page_size, offset=offset)
    )


def _parse_record_keys(key_type: str, record_keys: list[str]) -> list[str | int]:
    """Parse CLI record key strings into the dataset key type."""
    if key_type == "int":
        parsed_keys: list[str | int] = []
        for record_key in record_keys:
            try:
                parsed_keys.append(int(record_key))
            except ValueError as exc:
                raise typer.BadParameter(
                    f"Record key '{record_key}' is not a valid integer key."
                ) from exc
        return parsed_keys
    return list(record_keys)


# TODO Add a --format option to allow output in JSON or YAML. YAML is default for now.
# TODO allow turning off paged navigation and just output all records for a dataset - would use this for piping to other commands or files.
@app.command()
def browse(
    from_file: Annotated[
        Path,
        typer.Option(
            "--from",
            help="The path to the SQLite database file.",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
        ),
    ],
    dataset_name: Annotated[
        str | None,
        typer.Option(
            "--dataset",
            help="The dataset name to browse. Omit to list available datasets.",
        ),
    ] = None,
    page_size: Annotated[
        int,
        typer.Option(
            "--page-size",
            min=1,
            help="The number of records to show per page.",
        ),
    ] = 5,
    page: Annotated[
        int,
        typer.Option(
            "--page",
            min=1,
            help="The page number to display.",
        ),
    ] = 1,
    record_key: Annotated[
        list[str] | None,
        typer.Option(
            "--record-key",
            help="A record key to display. May be repeated.",
        ),
    ] = None,
    quiet: Annotated[
        bool,
        typer.Option(
            "--quiet",
            help="Suppress non-output messages.",
        ),
    ] = False,
    interactive: Annotated[
        bool,
        typer.Option(
            "--interactive/--no-interactive",
            help="Prompt for next/previous page navigation when browsing a dataset.",
        ),
    ] = False,
) -> None:
    """Browse the records from a SQLite database."""
    if quiet:
        messenger = Console(stderr=True, quiet=True)
    else:
        messenger = Console(stderr=True)
    stdout = Console()

    record_keys = [] if record_key is None else record_key
    interactive_mode = interactive or sys.stdin.isatty()

    with db_connection_manager(str(from_file), read_only=False) as connection:
        db_query = DatasetDbQuery(connection)

        if dataset_name is None:
            dataset_summary: dict[str, dict[str, int | str]] = {}
            for current_dataset_name in sorted(db_query.dataset_key_types):
                dataset_summary[current_dataset_name] = {
                    "record_count": db_query.dataset_record_count(current_dataset_name),
                    "key_type": db_query.dataset_key_types[current_dataset_name],
                }
            stdout.print(
                yaml_io.safe_dump_str(dataset_summary, sort_keys=False).rstrip()
            )
            return

        if dataset_name not in db_query.dataset_key_types:
            raise ValueError(
                f"Dataset '{dataset_name}' not found in the database. "
                "Ensure that the dataset has been loaded into the database."
            )

        key_type = db_query.dataset_key_types[dataset_name]
        total_records = db_query.dataset_record_count(dataset_name)
        page_count = max(1, (total_records + page_size - 1) // page_size)
        current_page = page

        if record_keys:
            records = _fetch_page_records(
                db_query,
                dataset_name=dataset_name,
                key_type=key_type,
                page=current_page,
                page_size=page_size,
                record_keys=record_keys,
            )
            page_mapping = _page_mapping_from_records(records)
            messenger.print(
                f"[bold blue]{dataset_name}[/bold blue] page {current_page} with {len(page_mapping)} of {total_records} records"
            )
            stdout.print(yaml_io.safe_dump_str(page_mapping, sort_keys=False).rstrip())
            return

        while True:
            records = _fetch_page_records(
                db_query,
                dataset_name=dataset_name,
                key_type=key_type,
                page=current_page,
                page_size=page_size,
            )
            page_mapping = _page_mapping_from_records(records)
            messenger.print(
                f"[bold blue]{dataset_name}[/bold blue] page {current_page}/{page_count} with {len(page_mapping)} of {total_records} records"
            )
            stdout.print(yaml_io.safe_dump_str(page_mapping, sort_keys=False).rstrip())
            if current_page >= page_count or not interactive_mode:
                return
            response = typer.prompt(
                "Next page? [n]ext, [p]revious, [q]uit",
                default="n",
                show_default=False,
            )
            match response.strip().lower():
                case "n" | "next" | "":
                    current_page += 1
                case "p" | "prev" | "previous":
                    current_page = max(1, current_page - 1)
                case "q" | "quit" | "exit":
                    return
                case _:
                    messenger.print("Please enter n, p, or q.")
