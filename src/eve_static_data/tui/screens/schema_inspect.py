"""Schema inspection screen for SDE datasets."""

import json
from pathlib import Path

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Static

from eve_static_data.helpers import schema_report
from eve_static_data.helpers.sde_info import load_sde_info_from_detected_file
from eve_static_data.tui.widgets.progress_log import ProgressLog
from eve_static_data.tui.widgets.text_viewer import TextViewer


class SchemaInspectScreen(Screen[None]):
    """Screen for schema scanning and report saving."""

    def compose(self) -> ComposeResult:
        """Compose schema inspection UI."""
        yield Header()
        yield Static("Schema Inspection", classes="section-title")
        yield Input(placeholder="SDE directory", id="sde-dir")
        yield Input(
            placeholder="Output directory (optional)",
            id="output-dir",
        )
        yield Button("Scan Schema", id="scan")
        yield ProgressLog(id="log")
        yield TextViewer(id="viewer")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle schema scan actions.

        Args:
            event: Button pressed event.
        """
        if event.button.id == "scan":
            self.run_worker(self._scan_schema(), exclusive=True, thread=True)

    def _scan_schema(self) -> None:
        """Scan schema paths and save JSON/markdown reports."""
        log = self.query_one("#log", ProgressLog)
        viewer = self.query_one("#viewer", TextViewer)
        sde_directory = Path(self.query_one("#sde-dir", Input).value.strip())
        output_text = self.query_one("#output-dir", Input).value.strip()
        try:
            info = load_sde_info_from_detected_file(sde_directory)
            output_dir = (
                Path(output_text) if output_text else (sde_directory / "schema")
            )
            output_dir.mkdir(parents=True, exist_ok=True)
            sde_format = (
                "yaml-model" if info["data_format"] == "YAML" else "jsonl-model"
            )
            report = schema_report.scan_directory(sde_directory, sde_format=sde_format)
            markdown = schema_report.generate_markdown_report(report)

            (output_dir / "schema_report.json").write_text(
                json.dumps(report, indent=2), encoding="utf-8"
            )
            (output_dir / "schema_report.md").write_text(markdown, encoding="utf-8")

            viewer.set_text(markdown)
            log.add_info(
                "Schema scan complete: "
                f"build={info['buildNumber']} release={info['releaseDate']} "
                f"format={sde_format} output={output_dir}"
            )
        except Exception as exc:
            log.add_error(f"Schema scan failed: {exc}")
