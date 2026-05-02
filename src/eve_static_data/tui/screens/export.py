"""Export screen for YAML to JSON and localization narrowing."""

import json
from pathlib import Path

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Static
from yaml import safe_load

from eve_static_data.helpers.sde_info import load_sde_info_from_detected_file
from eve_static_data.models.common import narrow_localizable_json_dict
from eve_static_data.tui.widgets.progress_log import ProgressLog
from eve_static_data.tui.widgets.text_viewer import TextViewer


class ExportScreen(Screen[None]):
    """Screen for conversion and localization export workflows."""

    def compose(self) -> ComposeResult:
        """Compose export UI."""
        yield Header()
        yield Static("Export", classes="section-title")
        yield Input(placeholder="Source SDE directory", id="source-dir")
        yield Input(placeholder="Output directory", id="output-dir")
        yield Input(
            placeholder="Languages csv (e.g. en,fr) for localization narrowing",
            id="langs",
            value="en",
        )
        yield Button("YAML -> JSON", id="yaml-json")
        yield Button("Narrow Localizations", id="localized")
        yield ProgressLog(id="log")
        yield TextViewer(id="viewer")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle export action triggers.

        Args:
            event: Button pressed event.
        """
        if event.button.id == "yaml-json":
            self.run_worker(self._yaml_to_json(), exclusive=True, thread=True)
        elif event.button.id == "localized":
            self.run_worker(self._localized_export(), exclusive=True, thread=True)

    def _yaml_to_json(self) -> None:
        """Convert YAML datasets to JSON files in the output directory."""
        log = self.query_one("#log", ProgressLog)
        viewer = self.query_one("#viewer", TextViewer)
        source_dir = Path(self.query_one("#source-dir", Input).value.strip())
        output_dir = Path(self.query_one("#output-dir", Input).value.strip())
        try:
            info = load_sde_info_from_detected_file(source_dir)
            if info["data_format"] != "YAML":
                raise ValueError(
                    "YAML->JSON export requires YAML-model source data format."
                )
            output_dir.mkdir(parents=True, exist_ok=True)
            converted = 0
            for yaml_path in sorted(source_dir.glob("*.yaml")):
                payload = safe_load(yaml_path.read_text(encoding="utf-8"))
                output_file = output_dir / f"{yaml_path.stem}.json"
                output_file.write_text(
                    json.dumps(payload, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
                converted += 1
            log.add_info(f"Converted {converted} YAML datasets to JSON.")
            viewer.set_text(
                f"Converted {converted} files\nsource={source_dir}\noutput={output_dir}"
            )
        except Exception as exc:
            log.add_error(f"YAML->JSON export failed: {exc}")

    def _localized_export(self) -> None:
        """Narrow localized fields in JSON datasets to selected languages."""
        log = self.query_one("#log", ProgressLog)
        viewer = self.query_one("#viewer", TextViewer)
        source_dir = Path(self.query_one("#source-dir", Input).value.strip())
        output_dir = Path(self.query_one("#output-dir", Input).value.strip())
        selected_langs = {
            part.strip()
            for part in self.query_one("#langs", Input).value.split(",")
            if part.strip()
        }
        try:
            info = load_sde_info_from_detected_file(source_dir)
            if info["file_format"] != "JSON":
                raise ValueError("Localization narrowing currently expects JSON files.")
            output_dir.mkdir(parents=True, exist_ok=True)
            converted = 0
            for json_path in sorted(source_dir.glob("*.json")):
                payload = json.loads(json_path.read_text(encoding="utf-8"))
                narrowed = narrow_localizable_json_dict(payload, selected_langs)
                output_file = output_dir / json_path.name
                output_file.write_text(
                    json.dumps(narrowed, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
                converted += 1
            log.add_info(
                f"Exported localized JSON for {converted} files using {sorted(selected_langs)}"
            )
            viewer.set_text(
                f"Localized export complete\nfiles={converted}\nlangs={sorted(selected_langs)}"
            )
        except Exception as exc:
            log.add_error(f"Localized export failed: {exc}")
