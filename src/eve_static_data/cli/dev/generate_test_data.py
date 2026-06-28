"""Generate small fixture datasets from local SDE files."""

from collections.abc import Iterator
from enum import Enum
from pathlib import Path
from typing import Annotated, Any

import typer

from eve_static_data.helpers import json_io
from eve_static_data.helpers.yaml_io import safe_dump_path, safe_load_path

app = typer.Typer(no_args_is_help=True)


class DatasetFormat(str, Enum):
    """Supported source dataset formats for fixture generation."""

    auto = "auto"
    yaml = "yaml"
    jsonl = "jsonl"


def _has_files(sde_path: Path, suffix: str) -> bool:
    """Return whether the directory contains at least one file with suffix."""
    return next(sde_path.glob(f"*{suffix}"), None) is not None


def _resolve_format(sde_path: Path, dataset_format: DatasetFormat) -> DatasetFormat:
    """Resolve auto format selection based on files present in the directory."""
    if dataset_format is not DatasetFormat.auto:
        return dataset_format

    if _has_files(sde_path, ".yaml"):
        return DatasetFormat.yaml
    if _has_files(sde_path, ".jsonl"):
        return DatasetFormat.jsonl

    raise typer.BadParameter(
        "No supported dataset files found. Expected .yaml or .jsonl files."
    )


def _first_items(data: dict[Any, Any], count: int) -> dict[Any, Any]:
    """Return a dictionary containing only the first ``count`` items."""
    result: dict[Any, Any] = {}
    for index, (record_key, record_value) in enumerate(data.items()):
        if index >= count:
            break
        result[record_key] = record_value
    return result


def _iter_first_lines(file_path: Path, count: int) -> Iterator[str]:
    """Yield the first non-empty lines from a file."""
    with file_path.open("r", encoding="utf-8") as file_handle:
        lines_written = 0
        for line in file_handle:
            if not line.strip():
                continue
            yield line
            lines_written += 1
            if lines_written >= count:
                break


def _write_text(path: Path, text: str, overwrite: bool) -> None:
    """Write text to a file with explicit overwrite behavior."""
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = "w" if overwrite else "x"
    with path.open(mode, encoding="utf-8") as file_handle:
        file_handle.write(text)


def _generate_yaml_test_data(
    sde_path: Path,
    output_path: Path,
    records_per_file: int,
    overwrite: bool,
) -> int:
    """Generate YAML and JSON fixture files from YAML SDE datasets."""
    yaml_output = output_path / "yaml"
    json_output = output_path / "json"
    generated_files = 0

    for yaml_input_file in sorted(sde_path.glob("*.yaml")):
        loaded_data = safe_load_path(yaml_input_file)
        if not isinstance(loaded_data, dict):
            continue

        fixture_data = _first_items(loaded_data, records_per_file)
        yaml_target = yaml_output / yaml_input_file.name
        json_target = json_output / f"{yaml_input_file.stem}.json"

        if not overwrite and (yaml_target.exists() or json_target.exists()):
            raise FileExistsError(
                f"Fixture output already exists for {yaml_input_file.name}. "
                "Use --overwrite to replace existing files."
            )

        yaml_target.parent.mkdir(parents=True, exist_ok=True)
        json_target.parent.mkdir(parents=True, exist_ok=True)
        safe_dump_path(fixture_data, yaml_target)
        _write_text(
            json_target,
            f"{json_io.json_dumps(fixture_data, indent=2)}\n",
            overwrite=overwrite,
        )
        generated_files += 1

    return generated_files


def _generate_jsonl_test_data(
    sde_path: Path,
    output_path: Path,
    records_per_file: int,
    overwrite: bool,
) -> int:
    """Generate JSONL fixture files from JSONL SDE datasets."""
    generated_files = 0

    for jsonl_input_file in sorted(sde_path.glob("*.jsonl")):
        target_file = output_path / jsonl_input_file.name

        if not overwrite and target_file.exists():
            raise FileExistsError(
                f"Fixture output already exists for {jsonl_input_file.name}. "
                "Use --overwrite to replace existing files."
            )

        first_lines = "".join(_iter_first_lines(jsonl_input_file, records_per_file))
        _write_text(target_file, first_lines, overwrite=overwrite)
        generated_files += 1

    return generated_files


@app.command(name="files")
def generate_files(
    sde_path: Annotated[
        Path,
        typer.Argument(
            help="Path to a directory containing SDE dataset files.",
            exists=True,
            file_okay=False,
            dir_okay=True,
            readable=True,
        ),
    ],
    output_path: Annotated[
        Path,
        typer.Argument(
            help="Directory where fixture files will be written.",
            file_okay=False,
            dir_okay=True,
        ),
    ],
    dataset_format: Annotated[
        DatasetFormat,
        typer.Option(
            "--format",
            help="Source dataset format. Defaults to auto detection.",
            case_sensitive=False,
        ),
    ] = DatasetFormat.auto,
    records_per_file: Annotated[
        int,
        typer.Option(
            "--records-per-file",
            min=1,
            help="Maximum number of records copied into each fixture file.",
        ),
    ] = 3,
    overwrite: Annotated[
        bool,
        typer.Option(
            "--overwrite",
            help="Overwrite existing fixture files when present.",
        ),
    ] = False,
) -> None:
    """Generate small fixture datasets from local SDE dataset files."""
    resolved_format = _resolve_format(sde_path, dataset_format)

    if resolved_format is DatasetFormat.yaml:
        generated_files = _generate_yaml_test_data(
            sde_path=sde_path,
            output_path=output_path,
            records_per_file=records_per_file,
            overwrite=overwrite,
        )
    else:
        generated_files = _generate_jsonl_test_data(
            sde_path=sde_path,
            output_path=output_path,
            records_per_file=records_per_file,
            overwrite=overwrite,
        )

    typer.echo(
        f"Generated {generated_files} fixture files from {resolved_format.value} datasets in {output_path}."
    )
