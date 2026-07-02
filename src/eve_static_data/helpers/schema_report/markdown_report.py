"""Render markdown output for schema inspection reports."""

from mdformat import text as mdformat_text  # type: ignore

from eve_static_data.helpers.schema_report.schema_report import SchemaReport


def generate_markdown_report(report: SchemaReport) -> str:
    """Render a human-readable markdown schema report.

    Args:
        report: Schema report from one or more datasets.

    Returns:
        Markdown text with a summary and per-dataset sections.
    """
    report_metadata = report["sde_metadata"]
    report_source_format = report_metadata.variant or "unknown"

    lines: list[str] = [
        "# Schema Report",
        "",
        "## Summary",
        f"- source_path: {report['source_path']}",
        f"- generated_at_utc: {report['generated_at_utc']}",
        (
            "- sde_metadata: "
            f"build number: {report_metadata.buildNumber}, "
            f"release date: {report_metadata.releaseDate}, "
            f"source format: {report_source_format}"
        ),
        f"- files_scanned: {report['file_count']}",
        f"- total_records: {report['total_records']}",
        f"- total_unique_paths: {report['total_unique_paths']}",
        "",
    ]

    for dataset_name in sorted(report["datasets"]):
        dataset = report["datasets"][dataset_name]
        dataset_metadata = dataset["sde_metadata"]
        dataset_source_format = dataset_metadata.variant or "unknown"
        key_type_summary = ", ".join(
            f"{type_name}:{count}"
            for type_name, count in dataset["top_level_key_type_counts"].items()
        )
        lines.extend([
            f"## {dataset['dataset_name']}",
            f"- dataset_source: {dataset['dataset_source']}",
            (
                "- sde_metadata: "
                f"build number: {dataset_metadata.buildNumber}, "
                f"release date: {dataset_metadata.releaseDate}, "
                f"source format: {dataset_source_format}"
            ),
            f"- Records: {dataset['total_records']}",
            f"- Top-level key types: {key_type_summary or 'unknown'}",
            f"- Valid dict records: {dataset['valid_record_count']}",
            f"- Skipped top-level items: {dataset['skipped_record_count']}",
            f"- Paths discovered: {dataset['path_count']}",
            "",
        ])

        if dataset["paths"]:
            lines.extend([
                "| Path | Presence | Required | Types |",
                "|------|----------|----------|-------|",
            ])
            for path in sorted(dataset["paths"]):
                row = dataset["paths"][path]
                type_summary = ", ".join(
                    f"{type_name}:{count}"
                    for type_name, count in row["value_type_counts"].items()
                )
                presence = f"{row['presence_count']}/{row['container_count']}"
                required = "yes" if row["required"] else "no"
                lines.append(f"| {path} | {presence} | {required} | {type_summary} |")
        else:
            lines.append("No schema paths discovered.")

        lines.append("")
        lines.append("### Warnings")
        lines.append("")
        if dataset["warnings"]:
            for warning in dataset["warnings"]:
                lines.append(f"- {warning}")
        else:
            lines.append("- None")
        lines.append("")

    result = "\n".join(lines).rstrip() + "\n"
    return mdformat_text(result, extensions=["tables"])
