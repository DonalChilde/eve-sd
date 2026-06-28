"""Generate small fixture datasets from local SDE files."""

from collections.abc import Iterator
from pathlib import Path
from typing import Annotated, Any, cast

import typer

from eve_static_data.helpers import json_io
from eve_static_data.helpers.sde_metadata import (
    SourceFormat,
    SourceMedia,
    load_sde_metadata,
)
from eve_static_data.helpers.yaml_io import safe_dump_path, safe_load_path

app = typer.Typer(no_args_is_help=True)


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


def _load_mapping_file(path: Path, source_media: SourceMedia) -> dict[Any, Any] | None:
    """Load a mapping dataset file based on source media."""
    if source_media is SourceMedia.YAML:
        loaded_data = safe_load_path(path)
    else:
        raise ValueError(
            f"Unsupported source media {source_media!r} for mapping dataset loading."
        )
    if not isinstance(loaded_data, dict):
        return None
    return cast(dict[Any, Any], loaded_data)


def _generate_yaml_test_data(
    sde_path: Path,
    output_path: Path,
    records_per_file: int,
    overwrite: bool,
    source_media: SourceMedia,
) -> int:
    """Generate YAML and JSON fixture files from YAML-model datasets."""
    if source_media is not SourceMedia.YAML:
        raise ValueError(
            f"Unsupported source media {source_media!r} for YAML-model fixture generation."
        )

    yaml_output = output_path / "yaml"
    json_output = output_path / "json"
    generated_files = 0
    glob_pattern = f"*{source_media.value}"

    for input_file in sorted(sde_path.glob(glob_pattern)):
        loaded_data = _load_mapping_file(input_file, source_media=source_media)
        if loaded_data is None:
            continue

        fixture_data = _first_items(loaded_data, records_per_file)
        yaml_target = yaml_output / f"{input_file.stem}.yaml"
        json_target = json_output / f"{input_file.stem}.json"

        if not overwrite and (yaml_target.exists() or json_target.exists()):
            raise FileExistsError(
                f"Fixture output already exists for {input_file.name}. "
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
    source_media: SourceMedia,
) -> int:
    """Generate JSONL fixture files from JSONL-model datasets."""
    if source_media is not SourceMedia.JSONL:
        raise ValueError(
            f"Unsupported source media {source_media!r} for JSONL-model fixture generation."
        )

    generated_files = 0
    glob_pattern = f"*{source_media.value}"

    for input_file in sorted(sde_path.glob(glob_pattern)):
        target_file = output_path / input_file.name
        if not overwrite and target_file.exists():
            raise FileExistsError(
                f"Fixture output already exists for {target_file.name}. "
                "Use --overwrite to replace existing files."
            )

        first_lines = "".join(_iter_first_lines(input_file, records_per_file))
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
    """Generate small fixture datasets from local SDE dataset files.

    This should replicate the structure of the original SDE datasets, but with a
    limited number of records per file for testing purposes.
    """
    try:
        sde_metadata = load_sde_metadata(sde_path)
    except (FileNotFoundError, ValueError) as exc:
        raise typer.BadParameter(str(exc)) from exc

    if sde_metadata.source_media not in {SourceMedia.YAML, SourceMedia.JSONL}:
        raise typer.BadParameter(
            "Test data generation requires original source datasets. "
            "Use a path containing _sde.yaml or _sde.jsonl metadata."
        )

    if sde_metadata.source_format is SourceFormat.YAML_MODEL:
        generated_files = _generate_yaml_test_data(
            sde_path=sde_path,
            output_path=output_path,
            records_per_file=records_per_file,
            overwrite=overwrite,
            source_media=sde_metadata.source_media,
        )
    else:
        generated_files = _generate_jsonl_test_data(
            sde_path=sde_path,
            output_path=output_path,
            records_per_file=records_per_file,
            overwrite=overwrite,
            source_media=sde_metadata.source_media,
        )

    typer.echo(
        "Generated "
        f"{generated_files} fixture files from {sde_metadata.source_format.value} "
        f"datasets ({sde_metadata.source_media.value}) in {output_path}."
    )
