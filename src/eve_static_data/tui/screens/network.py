"""Network operations screen for SDE APIs and downloads."""

import json
from pathlib import Path

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Static

from eve_static_data.helpers.sde_directory import load_sde_info
from eve_static_data.helpers.sde_info import SdeDatasetsInfo
from eve_static_data.tui.widgets.progress_log import ProgressLog
from eve_static_data.tui.widgets.text_viewer import TextViewer


class NetworkScreen(Screen[None]):
    """Screen for latest metadata, changelogs, and archive download."""

    def compose(self) -> ComposeResult:
        """Compose the network screen layout."""
        yield Header()
        yield Static("Network", classes="section-title")
        yield Static("Build number source")
        yield Input(placeholder="Build number (optional)", id="build-number")
        yield Input(
            placeholder="SDE directory (optional, for metadata source)",
            id="sde-dir",
        )
        yield Input(
            placeholder="Download output directory (for zip downloads)",
            id="download-output",
            value=".",
        )
        yield Input(placeholder="Variant: yaml or jsonl", id="variant", value="yaml")
        yield Input(
            placeholder="Save fetched text to file path (optional)",
            id="save-file",
        )
        yield Button("Fetch Latest Info", id="latest")
        yield Button("Fetch Schema Changelog", id="schema-changelog")
        yield Button("Fetch Data Changelog", id="data-changelog")
        yield Button("Download SDE Zip", id="download")
        yield ProgressLog(id="log")
        yield TextViewer(id="viewer")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle network action buttons.

        Args:
            event: Button pressed event.
        """
        if event.button.id == "latest":
            self.run_worker(self._fetch_latest(), exclusive=True)
        elif event.button.id == "schema-changelog":
            self.run_worker(self._fetch_schema_changelog(), exclusive=True)
        elif event.button.id == "data-changelog":
            self.run_worker(self._fetch_data_changelog(), exclusive=True)
        elif event.button.id == "download":
            self.run_worker(self._download_sde(), exclusive=True)

    async def _fetch_latest(self) -> None:
        """Fetch and display the latest SDE metadata payload."""
        log = self.query_one("#log", ProgressLog)
        viewer = self.query_one("#viewer", TextViewer)
        try:
            log.add_info("Fetching latest SDE info...")
            text = await self.app.sde_tools.fetch_latest_sde_info()
            viewer.set_text(text)
            self._save_text_if_requested(text)
            log.add_info("Latest info loaded.")
        except Exception as exc:
            log.add_error(f"Failed to fetch latest info: {exc}")

    async def _fetch_schema_changelog(self) -> None:
        """Fetch and display schema changelog text."""
        await self._fetch_changelog(kind="schema")

    async def _fetch_data_changelog(self) -> None:
        """Fetch and display data changelog text."""
        await self._fetch_changelog(kind="data")

    async def _fetch_changelog(self, kind: str) -> None:
        """Fetch changelog text by selected build number source.

        Args:
            kind: Changelog type, either ``schema`` or ``data``.
        """
        log = self.query_one("#log", ProgressLog)
        viewer = self.query_one("#viewer", TextViewer)
        try:
            build_number, sde_directory_info = await self._resolve_build_number()
            log.add_info(f"Fetching {kind} changelog for build {build_number}...")
            if kind == "schema":
                text = await self.app.sde_tools.fetch_schema_changelog(build_number)
                default_file = f"schema_changelog_{build_number}.yaml"
            else:
                text = await self.app.sde_tools.fetch_data_changes(build_number)
                default_file = f"data_changelog_{build_number}.jsonl"
            viewer.set_text(text)
            self._save_text_if_requested(text)
            if sde_directory_info is not None:
                self._save_text_to_directory_metadata(
                    sde_directory_info["directory"],
                    default_file,
                    text,
                )
            log.add_info(f"{kind.title()} changelog loaded.")
        except Exception as exc:
            log.add_error(f"Failed to fetch {kind} changelog: {exc}")

    async def _download_sde(self) -> None:
        """Download an SDE zip archive to the selected output path."""
        log = self.query_one("#log", ProgressLog)
        try:
            build_number, _ = await self._resolve_build_number()
            output_directory = Path(
                self.query_one("#download-output", Input).value.strip() or "."
            )
            variant = self.query_one("#variant", Input).value.strip() or "yaml"
            output_directory.mkdir(parents=True, exist_ok=True)
            log.add_info(
                f"Downloading build {build_number} ({variant}) to {output_directory}..."
            )
            output_path = await self.app.sde_tools.download(
                build_number=build_number,
                output_directory=output_directory,
                variant=variant,
                overwrite=False,
            )
            log.add_info(f"Downloaded: {output_path}")
        except Exception as exc:
            log.add_error(f"Download failed: {exc}")

    async def _resolve_build_number(
        self,
    ) -> tuple[int, dict[str, Path | SdeDatasetsInfo] | None]:
        """Resolve build number from user input, directory metadata, or latest API.

        Returns:
            Tuple of resolved build number and optional directory metadata details.
        """
        build_input = self.query_one("#build-number", Input).value.strip()
        if build_input:
            return int(build_input), None

        sde_directory_text = self.query_one("#sde-dir", Input).value.strip()
        if sde_directory_text:
            directory = Path(sde_directory_text)
            info = load_sde_info(directory)
            self.query_one("#log", ProgressLog).add_info(
                "Directory metadata: "
                f"build={info['buildNumber']} release={info['releaseDate']} "
                f"file={info['file_format']} data={info['data_format']}"
            )
            return info["buildNumber"], {"directory": directory, "info": info}

        latest_text = await self.app.sde_tools.fetch_latest_sde_info()
        latest_info = json.loads(latest_text)
        build_number = latest_info.get("buildNumber")
        if not isinstance(build_number, int):
            raise ValueError("Failed to resolve build number from latest API response.")
        return build_number, None

    def _save_text_if_requested(self, text: str) -> None:
        """Save text to explicit file path when user requested it.

        Args:
            text: Text payload to save.
        """
        save_path_value = self.query_one("#save-file", Input).value.strip()
        if not save_path_value:
            return
        save_path = Path(save_path_value)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_text(text, encoding="utf-8")
        self.query_one("#log", ProgressLog).add_info(f"Saved file: {save_path}")

    def _save_text_to_directory_metadata(
        self,
        sde_directory: Path,
        file_name: str,
        text: str,
    ) -> None:
        """Save fetched text under ``metadata/`` in the selected SDE directory.

        Args:
            sde_directory: Source SDE directory.
            file_name: Target file name under metadata directory.
            text: Text payload to write.
        """
        metadata_dir = sde_directory / "metadata"
        metadata_dir.mkdir(parents=True, exist_ok=True)
        output_file = metadata_dir / file_name
        output_file.write_text(text, encoding="utf-8")
        self.query_one("#log", ProgressLog).add_info(
            f"Saved metadata file: {output_file}"
        )
