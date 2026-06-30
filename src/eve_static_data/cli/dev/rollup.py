"""Rollup development command for schema report, validation, and changelog fetches."""

from pathlib import Path
from time import perf_counter
from typing import Annotated

import typer
from rich.console import Console

from eve_static_data.cli.helpers import get_esd_settings_from_context
from eve_static_data.helpers import json_io
from eve_static_data.helpers.http_client import config_http_client
from eve_static_data.helpers.save_text_file import save_text_file
from eve_static_data.helpers.schema_report.markdown_report import (
    generate_markdown_report as generate_schema_markdown_report,
)
from eve_static_data.helpers.schema_report.report_from_files import (
    get_json_schema_report,
    get_jsonl_schema_report,
    get_yaml_schema_report,
)
from eve_static_data.helpers.sde_metadata import (
    SourceMedia,
    load_sde_metadata,
)
from eve_static_data.helpers.settings_factory import sde_tools_factory

# from eve_static_data.validation.markdown_report import generate_markdown_report
# from eve_static_data.validation.validation_from_files import validate_yaml_datasets_file

app = typer.Typer(no_args_is_help=True)


@app.command(name="files")
def files(
    ctx: typer.Context,
    sde_path: Annotated[
        Path,
        typer.Argument(
            help="Path to a directory containing SDE dataset files and _sde metadata.",
            exists=True,
            file_okay=False,
            dir_okay=True,
            readable=True,
        ),
    ],
    output_dir: Annotated[
        Path,
        typer.Argument(
            help="Directory to write report, validation, and changelog files.",
            file_okay=False,
            dir_okay=True,
        ),
    ],
    overwrite: Annotated[
        bool,
        typer.Option(
            "--overwrite",
            help="Overwrite rollup output files if they already exist.",
        ),
    ] = False,
) -> None:
    """Generate schema report, validation report, and changelog files in one run."""
    start = perf_counter()
    console = Console()
    sde_metadata = load_sde_metadata(sde_path)
    console.print(
        f"Found {sde_metadata.source_format.value} datasets for build {sde_metadata.buildNumber} "
        f"with source media {sde_metadata.source_media.value} in {sde_path}. "
        f"Writing rollup output to {output_dir}."
    )
    build_suffix = str(sde_metadata.buildNumber)
    dataset_format = sde_metadata.source_format.value
    start_schema_report = perf_counter()
    if sde_metadata.source_media is SourceMedia.YAML:
        schema_report = get_yaml_schema_report(sde_path)
    elif sde_metadata.source_media is SourceMedia.JSONL:
        schema_report = get_jsonl_schema_report(sde_path)
    elif sde_metadata.source_media is SourceMedia.JSON:
        schema_report = get_json_schema_report(sde_path)
    else:
        raise typer.BadParameter(
            f"Unsupported source media {sde_metadata.source_media!r} for schema rollup."
        )

    schema_markdown = generate_schema_markdown_report(schema_report)
    save_text_file(
        text=json_io.json_dumps(schema_report, indent=2),
        output_dir=output_dir,
        file_name=f"schema_report_{dataset_format}_{build_suffix}.json",
        overwrite=overwrite,
    )
    save_text_file(
        text=schema_markdown,
        output_dir=output_dir,
        file_name=f"schema_report_{dataset_format}_{build_suffix}.md",
        overwrite=overwrite,
    )
    console.print(
        f"Schema report generated in {perf_counter() - start_schema_report:.2f} seconds."
    )
    # start_validation = perf_counter()
    # if sde_metadata.source_format is SourceFormat.JSONL_MODEL:
    #     raise typer.BadParameter(
    #         "Validation rollup currently supports YAML-model datasets only. "
    #         "Use an SDE path whose metadata reports source_format as yaml-model."
    #     )

    # validation_summary = validate_yaml_datasets_file(sde_path)
    # validation_markdown = generate_markdown_report(validation_summary)
    # save_text_file(
    #     text=json.dumps(asdict(validation_summary), indent=2, default=_json_default),
    #     output_dir=output_dir,
    #     file_name=f"yaml_validation_result_{build_suffix}.json",
    #     overwrite=overwrite,
    # )
    # save_text_file(
    #     text=validation_markdown,
    #     output_dir=output_dir,
    #     file_name=f"yaml_validation_report_{build_suffix}.md",
    #     overwrite=overwrite,
    # )
    # console.print(
    #     f"Validation report generated in {perf_counter() - start_validation:.2f} seconds."
    # )
    start_downloads = perf_counter()
    settings = get_esd_settings_from_context(ctx)
    session = config_http_client()
    sde_tools = sde_tools_factory(settings)
    schema_changes = sde_tools.fetch_schema_changelog(
        build_number=sde_metadata.buildNumber,
        session=session,
    )
    data_changes = sde_tools.fetch_data_changes(
        build_number=sde_metadata.buildNumber,
        session=session,
    )
    save_text_file(
        text=schema_changes,
        output_dir=output_dir,
        file_name=f"schema_changes_{build_suffix}.yaml",
        overwrite=overwrite,
    )
    save_text_file(
        text=data_changes,
        output_dir=output_dir,
        file_name=f"data_changes_{build_suffix}.jsonl",
        overwrite=overwrite,
    )
    console.print(
        f"Changelog files downloaded in {perf_counter() - start_downloads:.2f} seconds."
    )
    console.print(f"Rollup completed in {perf_counter() - start:.2f} seconds.")

    typer.echo(
        "Rollup complete. Wrote schema report, validation report, and changelog files "
        f"for build {build_suffix} to {output_dir}."
    )
