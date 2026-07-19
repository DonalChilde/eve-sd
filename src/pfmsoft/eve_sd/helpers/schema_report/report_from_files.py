"""Generate a schema report from SDE data files in a directory."""

from collections.abc import Iterable
from pathlib import Path

from pfmsoft.eve_snippets import json_io, yaml_io

from pfmsoft.eve_sd.helpers.schema_report.markdown_report import (
    generate_markdown_report,
)
from pfmsoft.eve_sd.helpers.schema_report.schema_report import (
    DatasetInput,
    SchemaReport,
    build_schema_report,
)
from pfmsoft.eve_sd.helpers.sde_metadata import load_sde_metadata

# TODO use raw loader helpers, record types


def get_jsonl_schema_report(sde_directory: Path) -> SchemaReport:
    """Generate a schema report from all JSONL datasets in a directory."""
    sde_metadata = load_sde_metadata(sde_directory)

    def dataset_input_generator() -> Iterable[DatasetInput]:
        for dataset_file in sde_directory.glob("*.jsonl"):
            dataset_name = dataset_file.stem

            data = {x["_key"]: x for x in json_io.jsonl_load_path(dataset_file)}
            yield DatasetInput(
                dataset_name=dataset_name,
                dataset_data=data,
                sde_metadata=sde_metadata,
            )

    return build_schema_report(
        datasets=dataset_input_generator(),
        sde_metadata=sde_metadata,
        dataset_source=str(sde_directory),
    )


def get_yaml_schema_report(sde_directory: Path) -> SchemaReport:
    """Generate a schema report from all YAML datasets in a directory."""
    sde_metadata = load_sde_metadata(sde_directory)

    def dataset_input_generator() -> Iterable[DatasetInput]:
        for dataset_file in sde_directory.glob("*.yaml"):
            dataset_name = dataset_file.stem

            data = yaml_io.safe_load_path(dataset_file)
            yield DatasetInput(
                dataset_name=dataset_name,
                dataset_data=data,
                sde_metadata=sde_metadata,
            )

    return build_schema_report(
        datasets=dataset_input_generator(),
        sde_metadata=sde_metadata,
        dataset_source=str(sde_directory),
    )


def get_json_schema_report(sde_directory: Path) -> SchemaReport:
    """Generate a schema report from all JSON datasets in a directory.

    This would be used when the original yaml or jsonl datasets have been converted to
    JSON dicts. Note that the sde_format must be specified to indicate the original format of the data.
    """
    sde_metadata = load_sde_metadata(sde_directory)

    def dataset_input_generator() -> Iterable[DatasetInput]:
        for dataset_file in sde_directory.glob("*.json"):
            dataset_name = dataset_file.stem

            data = json_io.json_load_path(dataset_file)
            yield DatasetInput(
                dataset_name=dataset_name,
                dataset_data=data,
                sde_metadata=sde_metadata,
            )

    return build_schema_report(
        datasets=dataset_input_generator(),
        sde_metadata=sde_metadata,
        dataset_source=str(sde_directory),
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate a schema report from SDE data files."
    )
    parser.add_argument(
        "sde_directory", type=Path, help="Path to the SDE data directory."
    )
    parser.add_argument(
        "-f",
        "--sde-format",
        type=str,
        choices=["yaml-model", "jsonl-model"],
        help="Original format of the JSON data.",
    )
    args = parser.parse_args()

    if args.sde_directory.glob("*.jsonl"):
        report = get_jsonl_schema_report(args.sde_directory)

    elif args.sde_directory.glob("*.yaml"):
        report = get_yaml_schema_report(args.sde_directory)
    elif args.sde_directory.glob("*.json"):
        report = get_json_schema_report(args.sde_directory)
    else:
        raise ValueError("No supported data files found in the specified directory.")

    markdown_report = generate_markdown_report(report)
    print(markdown_report)
