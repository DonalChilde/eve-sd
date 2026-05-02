"""Dataset browser screen for unpacked SDE directories."""

import json
from pathlib import Path
from typing import Any

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Static
from yaml import safe_load

from eve_static_data.helpers.sde_info import SdeDatasetsInfo
from eve_static_data.models.dataset_filenames import SdeDatasetFiles
from eve_static_data.tui.widgets.dataset_list import DatasetList
from eve_static_data.tui.widgets.progress_log import ProgressLog
from eve_static_data.tui.widgets.record_viewer import RecordViewer


class BrowserScreen(Screen[None]):
    """Screen for listing and viewing dataset files in an SDE directory."""

    def __init__(self) -> None:
        """Initialize browser state."""
        super().__init__()
        self._current_directory: Path | None = None
        self._current_format_suffix = ".yaml"
        self._known_stems = {dataset.value for dataset in SdeDatasetFiles}

    def compose(self) -> ComposeResult:
        """Compose the browser layout."""
        yield Header()
        yield Static("Dataset Browser", classes="section-title")
        yield Input(placeholder="SDE directory", id="sde-dir")
        yield Static("Mode: raw or parsed", classes="muted")
        yield Input(placeholder="Mode", id="mode", value="raw")
        yield Input(placeholder="Page size", id="page-size", value="50")
        yield Button("Load Directory", id="load")
        yield Button("Open Selected", id="open")
        yield Button("Prev Page", id="prev")
        yield Button("Next Page", id="next")
        yield DatasetList(id="datasets")
        yield ProgressLog(id="log")
        yield RecordViewer(id="viewer")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle screen actions.

        Args:
            event: Button pressed event.
        """
        button_id = event.button.id
        if button_id == "load":
            self.run_worker(self._load_directory(), exclusive=True, thread=True)
        elif button_id == "open":
            self.run_worker(self._open_selected(), exclusive=True, thread=True)
        elif button_id == "prev":
            self.query_one("#viewer", RecordViewer).previous_page()
        elif button_id == "next":
            self.query_one("#viewer", RecordViewer).next_page()

    def _load_directory(self) -> None:
        """Load directory metadata and populate list of dataset files."""
        log = self.query_one("#log", ProgressLog)
        directory_value = self.query_one("#sde-dir", Input).value.strip()
        if not directory_value:
            log.add_error("Provide an SDE directory path.")
            return
        directory = Path(directory_value)
        try:
            info = self._load_info(directory)
            self._current_directory = directory
            suffix_lookup = {"YAML": ".yaml", "JSONL": ".jsonl", "JSON": ".json"}
            self._current_format_suffix = suffix_lookup[info["file_format"]]
            files = self._dataset_files(directory, self._current_format_suffix)
            self.query_one("#datasets", DatasetList).set_files(files)
            log.add_info(
                "Loaded directory metadata: "
                f"build={info['buildNumber']} release={info['releaseDate']} "
                f"file={info['file_format']} data={info['data_format']}"
            )
        except Exception as exc:
            log.add_error(f"Failed to load directory: {exc}")

    def _open_selected(self) -> None:
        """Open selected dataset file in raw or parsed mode."""
        log = self.query_one("#log", ProgressLog)
        if self._current_directory is None:
            log.add_error("Load a directory before opening files.")
            return

        option_list = self.query_one("#datasets", DatasetList)
        selected = option_list.get_option_at_index(option_list.highlighted)
        if selected is None:
            log.add_error("No dataset is selected.")
            return

        stem = str(selected.prompt).replace(" [unknown]", "")
        file_path = self._current_directory / f"{stem}{self._current_format_suffix}"
        if not file_path.is_file():
            log.add_error(f"Dataset file not found: {file_path}")
            return

        mode = self.query_one("#mode", Input).value.strip().lower() or "raw"
        page_size_text = self.query_one("#page-size", Input).value.strip() or "50"
        page_size = max(int(page_size_text), 1)

        viewer = self.query_one("#viewer", RecordViewer)
        viewer.page_size = page_size
        try:
            if mode == "parsed" and stem in self._known_stems:
                content = self._load_parsed_view(file_path)
            else:
                content = self._load_raw_view(file_path)
            viewer.set_content(content)
            log.add_info(f"Opened {file_path.name} in {mode} mode.")
        except Exception as exc:
            log.add_error(f"Failed to open dataset: {exc}")

    def _load_info(self, directory: Path) -> SdeDatasetsInfo:
        """Load SDE metadata from the selected directory.

        Args:
            directory: Directory containing ``_sde.*`` metadata file.

        Returns:
            Parsed SDE metadata dictionary.
        """
        from eve_static_data.helpers.sde_info import load_sde_info_from_detected_file

        return load_sde_info_from_detected_file(directory)

    def _dataset_files(self, directory: Path, suffix: str) -> list[Path]:
        """Return dataset files matching the active suffix.

        Args:
            directory: Directory to inspect.
            suffix: Active file extension.

        Returns:
            Matching dataset files excluding ``_sde.*``.
        """
        return [
            path
            for path in directory.glob(f"*{suffix}")
            if path.is_file() and path.stem != SdeDatasetFiles.SDE_INFO.value
        ]

    def _load_raw_view(self, file_path: Path) -> str:
        """Load a file with line-preserving raw mode and optional pretty JSON.

        Args:
            file_path: Dataset path to read.

        Returns:
            Viewer-ready text payload.
        """
        if file_path.suffix == ".jsonl":
            lines: list[str] = []
            for line in file_path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                try:
                    lines.append(
                        json.dumps(json.loads(line), indent=2, ensure_ascii=False)
                    )
                except json.JSONDecodeError:
                    lines.append(line)
            return "\n\n".join(lines)
        return file_path.read_text(encoding="utf-8")

    def _load_parsed_view(self, file_path: Path) -> str:
        """Load parsed summary content for known dataset files.

        Args:
            file_path: Dataset path.

        Returns:
            Pretty formatted parsed payload.
        """
        payload: Any
        if file_path.suffix in {".yaml", ".yml"}:
            payload = safe_load(file_path.read_text(encoding="utf-8"))
        elif file_path.suffix == ".json":
            payload = json.loads(file_path.read_text(encoding="utf-8"))
        else:
            records = [
                json.loads(line)
                for line in file_path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            payload = records
        return json.dumps(payload, indent=2, ensure_ascii=False, default=str)
