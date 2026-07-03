"""Tests for eve_sd.cli.main_typer."""

from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from typer.testing import CliRunner

from eve_sd import __app_name__, __url__, __version__
from eve_sd.cli import main_typer

runner = CliRunner()


@dataclass(slots=True)
class DummySettings:
    """Minimal settings object for CLI callback tests."""

    logging_directory: str


class TestMainTyperApp:
    """Tests for the top-level Typer application."""

    def test_default_options_populates_context_and_logs_startup(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        """Default options stores settings in context and configures logging."""
        settings = DummySettings(logging_directory=str(tmp_path / "logs"))
        configured_log_dirs: list[Path] = []
        logger_info = Mock()
        ctx = SimpleNamespace(obj=None)

        def fake_get_settings() -> DummySettings:
            """Return deterministic settings for the CLI callback."""
            return settings

        def fake_setup_logging(*, log_dir: Path) -> None:
            """Capture the configured log directory."""
            configured_log_dirs.append(log_dir)

        monkeypatch.setattr(main_typer, "get_settings", fake_get_settings)
        monkeypatch.setattr(main_typer, "setup_logging", fake_setup_logging)
        monkeypatch.setattr(main_typer.logger, "info", logger_info)

        main_typer.default_options(ctx)

        assert ctx.obj == {"esd-settings": settings}
        assert configured_log_dirs == [Path(settings.logging_directory)]
        logger_info.assert_called_once_with("Starting Eve SD v0.4.0")

    def test_help_lists_primary_commands(self) -> None:
        """Top-level help shows the primary command groups and commands."""
        result = runner.invoke(main_typer.app, ["--help"])

        assert result.exit_code == 0
        assert "Work with EVE Online static data" in result.stdout
        assert "fetch" in result.stdout
        assert "db" in result.stdout
        assert "export" in result.stdout
        assert "schema" in result.stdout
        assert "dev" in result.stdout
        assert "version" in result.stdout
        assert "settings" in result.stdout

    def test_version_command_prints_version_and_project_url(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        """Version prints the application version and project URL."""
        settings = DummySettings(logging_directory=str(tmp_path / "logs"))

        def fake_get_settings() -> DummySettings:
            """Return deterministic settings for the CLI callback."""
            return settings

        def fake_setup_logging(*, log_dir: Path) -> None:
            """Avoid real logging setup during CLI tests."""
            del log_dir

        monkeypatch.setattr(main_typer, "get_settings", fake_get_settings)
        monkeypatch.setattr(main_typer, "setup_logging", fake_setup_logging)

        result = runner.invoke(main_typer.app, ["version"])

        assert result.exit_code == 0
        assert f"{__app_name__} v{__version__}" in result.stdout
        assert f"Project URL: {__url__}" in result.stdout

    def test_docs_command_prints_bundled_documentation(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        """Docs prints the bundled documentation to stdout."""
        settings = DummySettings(logging_directory=str(tmp_path / "logs"))

        def fake_get_settings() -> DummySettings:
            """Return deterministic settings for the CLI callback."""
            return settings

        def fake_setup_logging(*, log_dir: Path) -> None:
            """Avoid real logging setup during CLI tests."""
            del log_dir

        monkeypatch.setattr(main_typer, "get_settings", fake_get_settings)
        monkeypatch.setattr(main_typer, "setup_logging", fake_setup_logging)

        result = runner.invoke(main_typer.app, ["docs"])

        assert result.exit_code == 0
        assert "EVE SD Documentation" in result.stdout
        assert "The CLI entrypoint command is:" in result.stdout

    def test_settings_command_initializes_shared_context(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        """Settings succeeds only when the callback seeds shared context."""
        settings = DummySettings(logging_directory=str(tmp_path / "logs"))
        configured_log_dirs: list[Path] = []

        def fake_get_settings() -> DummySettings:
            """Return deterministic settings for the CLI callback."""
            return settings

        def fake_setup_logging(*, log_dir: Path) -> None:
            """Capture the configured log directory."""
            configured_log_dirs.append(log_dir)

        monkeypatch.setattr(main_typer, "get_settings", fake_get_settings)
        monkeypatch.setattr(main_typer, "setup_logging", fake_setup_logging)

        result = runner.invoke(main_typer.app, ["settings"])

        assert result.exit_code == 0
        assert configured_log_dirs == [Path(settings.logging_directory)]
        assert "DummySettings" in result.stdout
        assert "User Agent:" in result.stdout
