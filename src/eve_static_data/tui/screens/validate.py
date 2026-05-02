"""Validation screen for SDE dataset model checks."""

from pathlib import Path

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Static

from eve_static_data.helpers.sde_info import load_sde_info_from_detected_file
from eve_static_data.tui.widgets.progress_log import ProgressLog
from eve_static_data.tui.widgets.text_viewer import TextViewer
from eve_static_data.yaml_validation import validate_yaml_datasets


class ValidateScreen(Screen[None]):
    """Screen for validating unpacked SDE directories."""

    def compose(self) -> ComposeResult:
        """Compose validation UI."""
        yield Header()
        yield Static("Validate", classes="section-title")
        yield Input(placeholder="SDE directory", id="sde-dir")
        yield Input(
            placeholder="Report directory (optional)",
            id="report-dir",
        )
        yield Button("Validate YAML Model", id="validate-yaml")
        yield ProgressLog(id="log")
        yield TextViewer(id="viewer")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Start selected validation workflow.

        Args:
            event: Button pressed event.
        """
        if event.button.id == "validate-yaml":
            self.run_worker(self._validate_yaml(), exclusive=True)

    async def _validate_yaml(self) -> None:
        """Run YAML-model validation and display summary output."""
        log = self.query_one("#log", ProgressLog)
        viewer = self.query_one("#viewer", TextViewer)
        sde_directory = Path(self.query_one("#sde-dir", Input).value.strip())
        report_directory_text = self.query_one("#report-dir", Input).value.strip()
        try:
            info = load_sde_info_from_detected_file(sde_directory)
            report_directory = (
                Path(report_directory_text)
                if report_directory_text
                else sde_directory / "validation"
            )
            log.add_info(
                "Validation metadata: "
                f"build={info['buildNumber']} release={info['releaseDate']} "
                f"file={info['file_format']} data={info['data_format']}"
            )
            result = await validate_yaml_datasets(
                sde_path=sde_directory,
                output_path=report_directory,
                sde_tools=self.app.sde_tools,
                overwrite=True,
            )
            viewer.set_text(str(result))
            log.add_info(f"Validation complete. Reports in {report_directory}")
        except Exception as exc:
            log.add_error(f"Validation failed: {exc}")
