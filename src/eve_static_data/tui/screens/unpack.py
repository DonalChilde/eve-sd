"""Unpack screen for archive extraction workflows."""

from pathlib import Path

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Static

from eve_static_data.tui.widgets.progress_log import ProgressLog
from eve_static_data.tui.widgets.text_viewer import TextViewer


class UnpackScreen(Screen[None]):
    """Screen for unpacking downloaded SDE zip archives."""

    def compose(self) -> ComposeResult:
        """Compose the unpack screen layout."""
        yield Header()
        yield Static("Unpack", classes="section-title")
        yield Input(placeholder="Path to SDE zip file", id="zip-path")
        yield Input(placeholder="Output directory", id="output-dir", value=".")
        yield Input(
            placeholder="Use build number directory? true/false",
            id="use-build-number",
            value="true",
        )
        yield Button("Unpack", id="unpack")
        yield ProgressLog(id="log")
        yield TextViewer(id="viewer")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle unpack button clicks.

        Args:
            event: Button pressed event.
        """
        if event.button.id == "unpack":
            self.run_worker(self._unpack_archive(), exclusive=True, thread=True)

    def _unpack_archive(self) -> None:
        """Run archive unpack operation and display resulting metadata."""
        log = self.query_one("#log", ProgressLog)
        viewer = self.query_one("#viewer", TextViewer)
        zip_path = Path(self.query_one("#zip-path", Input).value.strip())
        output_dir = Path(self.query_one("#output-dir", Input).value.strip() or ".")
        use_build_number = (
            self.query_one("#use-build-number", Input).value.strip().lower() != "false"
        )
        try:
            sde_path, info = self.app.sde_tools.unpack(
                input_path=zip_path,
                output_path=output_dir,
                use_build_number=use_build_number,
            )
            viewer.set_text(
                "\n".join(
                    [
                        f"Unpacked to: {sde_path}",
                        f"Build: {info['buildNumber']}",
                        f"Release Date: {info['releaseDate']}",
                        f"File Format: {info['file_format']}",
                        f"Data Format: {info['data_format']}",
                    ]
                )
            )
            log.add_info(f"Unpacked archive to {sde_path}")
        except Exception as exc:
            log.add_error(f"Unpack failed: {exc}")
