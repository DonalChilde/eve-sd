"""Tests for development CLI command registration and basic behavior."""

from pathlib import Path

from typer.testing import CliRunner

from eve_static_data.cli.main_typer import app

runner = CliRunner()


def test_root_help_includes_dev_command() -> None:
    """The top-level CLI should list the dev command group."""
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "dev" in result.stdout


def test_dev_help_includes_expected_subcommands() -> None:
    """The dev group should expose schema-report and generate-test-data commands."""
    result = runner.invoke(app, ["dev", "--help"])

    assert result.exit_code == 0
    assert "schema-report" in result.stdout
    assert "generate-test-data" in result.stdout


def test_schema_report_files_fails_for_empty_directory(tmp_path: Path) -> None:
    """Schema report generation should fail when no supported files are present."""
    result = runner.invoke(app, ["dev", "schema-report", "files", str(tmp_path)])

    assert result.exit_code == 2
    assert isinstance(result.exception, SystemExit)


def test_generate_test_data_files_fails_for_empty_directory(tmp_path: Path) -> None:
    """Fixture generation should fail when no supported files are present."""
    result = runner.invoke(
        app,
        ["dev", "generate-test-data", "files", str(tmp_path), str(tmp_path / "out")],
    )

    assert result.exit_code == 2
    assert isinstance(result.exception, SystemExit)
