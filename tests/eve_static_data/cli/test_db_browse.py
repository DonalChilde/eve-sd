"""Tests for the DB browse CLI command."""

from pathlib import Path

from typer.testing import CliRunner

from eve_static_data.cli.db import app
from eve_static_data.db.helpers import (
    create_read_write_connection,
    write_int_records,
    write_key_types,
    write_str_records,
)
from eve_static_data.db.load_datasets import write_db_metadata
from eve_static_data.db.models_2 import (
    DatasetRecordIntYaml,
    DatasetRecordStrYaml,
    SerializationFormat,
)
from eve_static_data.helpers.sde_metadata import SdeMetadata, SdeVariant, SourceMedia

runner = CliRunner()


def _create_test_database(db_path: Path) -> Path:
    with create_read_write_connection(str(db_path)) as connection:
        write_key_types(
            connection,
            dataset_key_types={"types": "int", "characterTitles": "str"},
        )
        write_db_metadata(
            connection,
            sde_metadata=SdeMetadata(
                buildNumber=1,
                releaseDate="2026-01-01T00:00:00Z",
                variant=SdeVariant.YAML,
                source_media=SourceMedia.YAML,
            ),
            serialization_format=SerializationFormat.YAML,
        )
        write_int_records(
            connection,
            records=(
                DatasetRecordIntYaml.from_record(
                    "types", 10, {"typeID": 10, "name": "Ten"}
                ),
                DatasetRecordIntYaml.from_record(
                    "types", 20, {"typeID": 20, "name": "Twenty"}
                ),
                DatasetRecordIntYaml.from_record(
                    "types", 30, {"typeID": 30, "name": "Thirty"}
                ),
            ),
        )
        write_str_records(
            connection,
            records=(
                DatasetRecordStrYaml.from_record(
                    "characterTitles", "a", {"titleID": "a", "name": "Alpha"}
                ),
                DatasetRecordStrYaml.from_record(
                    "characterTitles", "b", {"titleID": "b", "name": "Beta"}
                ),
            ),
        )
    return db_path


def test_browse_lists_datasets(tmp_path: Path) -> None:
    db_path = _create_test_database(tmp_path / "browse.db")

    result = runner.invoke(app, ["browse", "--from", str(db_path)])

    assert result.exit_code == 0
    assert "types" in result.stdout
    assert "record_count: 3" in result.stdout
    assert "characterTitles" in result.stdout


def test_browse_prints_record_page(tmp_path: Path) -> None:
    db_path = _create_test_database(tmp_path / "browse.db")

    result = runner.invoke(
        app,
        ["browse", "--from", str(db_path), "--dataset", "types", "--page-size", "2"],
    )

    assert result.exit_code == 0
    assert "10:" in result.stdout
    assert "20:" in result.stdout
    assert "30:" not in result.stdout


def test_browse_can_advance_to_next_page(tmp_path: Path) -> None:
    db_path = _create_test_database(tmp_path / "browse.db")

    result = runner.invoke(
        app,
        [
            "browse",
            "--from",
            str(db_path),
            "--dataset",
            "types",
            "--page-size",
            "2",
            "--interactive",
        ],
        input="n\nq\n",
    )

    assert result.exit_code == 0
    assert "10:" in result.stdout
    assert "20:" in result.stdout
    assert "30:" in result.stdout


def test_browse_prints_explicit_record_keys(tmp_path: Path) -> None:
    db_path = _create_test_database(tmp_path / "browse.db")

    result = runner.invoke(
        app,
        [
            "browse",
            "--from",
            str(db_path),
            "--dataset",
            "characterTitles",
            "--record-key",
            "b",
            "--record-key",
            "a",
        ],
    )

    assert result.exit_code == 0
    assert "a:" in result.stdout
    assert "b:" in result.stdout
