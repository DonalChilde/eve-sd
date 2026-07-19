"""Network and archive helpers for EVE SD workflows."""

# Refactor note: this class may be simplified into function-based helpers in a
# future cleanup if stateful behavior remains unnecessary.

from pathlib import Path
from string import Template

from httpx2 import Client

from pfmsoft.eve_sd import (
    DATA_CHANGES_URL_TEMPLATE,
    DATA_FILENAME_TEMPLATE,
    LATEST_INFO_URL,
    SCHEMA_CHANGELOG_URL,
    SDE_URL_TEMPLATE,
    USER_AGENT,
)
from pfmsoft.eve_sd.helpers.httpx2.download_files import (
    download_bytes_to_file,
    download_text,
)
from pfmsoft.eve_sd.helpers.sde_metadata import SdeMetadata
from pfmsoft.eve_sd.helpers.sde_unpack import unpack as unpack_sde


class SDETools:
    """Facade for downloading and unpacking EVE SD resources."""

    def __init__(
        self,
        latest_info_url: str = LATEST_INFO_URL,
        download_url_template: str = SDE_URL_TEMPLATE,
        data_changes_url_template: str = DATA_CHANGES_URL_TEMPLATE,
        schema_changelog_url: str = SCHEMA_CHANGELOG_URL,
        data_filename_template: str = DATA_FILENAME_TEMPLATE,
        user_agent: str = USER_AGENT,
    ):
        """Initialize endpoint templates and request defaults for SDE workflows.

        Args:
            latest_info_url: Endpoint template for latest SDE metadata.
            download_url_template: Endpoint template for downloadable SDE archives.
            data_changes_url_template: Endpoint template for data-change JSONL.
            schema_changelog_url: Endpoint template for schema changelog YAML.
            data_filename_template: Template for downloaded archive file names.
            user_agent: User-Agent header value sent with requests.
        """
        self.latest_info_url = latest_info_url
        self.download_url_template = download_url_template
        self.data_changes_url_template = data_changes_url_template
        self.schema_changelog_url = schema_changelog_url
        self.data_filename_template = data_filename_template
        self.user_agent = user_agent

    def download(
        self,
        build_number: int,
        output_directory: Path,
        *,
        session: Client,
        variant: str = "yaml",
        overwrite: bool = False,
    ) -> Path:
        """Download an SDE archive to a local directory.

        Args:
            build_number: SDE build number to download.
            output_directory: Directory where the archive file will be written.
            session: Reusable HTTP client session.
            variant: Archive variant, usually ``yaml`` or ``jsonl``.
            overwrite: Whether to replace an existing target file.

        Returns:
            Path to the downloaded archive file.
        """
        headers = {"User-Agent": self.user_agent}
        url = Template(self.download_url_template).substitute(
            build_number=build_number, variant=variant
        )
        file_name = Template(self.data_filename_template).substitute(
            build_number=build_number, variant=variant
        )
        output_path = output_directory / file_name
        download_bytes_to_file(
            url=url,
            file_path=output_path,
            headers=headers,
            overwrite=overwrite,
            session=session,
        )
        return output_path

    def unpack(
        self, input_path: Path, output_path: Path, use_build_number: bool = False
    ) -> tuple[Path, SdeMetadata]:
        """Unpack a downloaded SDE archive and return its metadata.

        Args:
            input_path: Path to the SDE zip archive.
            output_path: Base output directory for unpacked files.
            use_build_number: Whether to place extracted files in a build-number
                subdirectory.

        Returns:
            Tuple of ``(unpack_directory, sde_metadata)``.
        """
        file_path, info = unpack_sde(
            input_path, output_path, use_build_number=use_build_number
        )
        return file_path, info

    def validate(self, sde_path: Path, report_directory: Path) -> None:
        """Validate local SDE data and emit a report.

        Note:
            This method is currently not implemented.
        """
        raise NotImplementedError("SDE validation is not yet implemented.")

    def fetch_data_changes(self, build_number: int, *, session: Client) -> str:
        """Fetch SDE data changes JSONL text for a build number.

        The response is returned as raw JSONL text. Each non-empty line can be
        parsed with ``json.loads``.

        Args:
            build_number: SDE build number to fetch changes for.
            session: Reusable HTTP client session.

        Returns:
            Raw JSONL changelog text.
        """
        headers = {"User-Agent": self.user_agent}
        url = Template(self.data_changes_url_template).substitute(
            build_number=build_number
        )
        text, _ = download_text(url=url, headers=headers, session=session)
        return text

    def fetch_schema_changelog(self, build_number: int, *, session: Client) -> str:
        """Fetch schema changelog YAML text for a build number.

        Args:
            build_number: SDE build number to fetch schema changes for.
            session: Reusable HTTP client session.

        Returns:
            Raw YAML changelog text.
        """
        headers = {"User-Agent": self.user_agent}
        url = Template(self.schema_changelog_url).substitute(build_number=build_number)
        text, _ = download_text(url=url, headers=headers, session=session)
        return text

    def fetch_latest_sde_info(self, *, session: Client) -> str:
        """Fetch raw latest-SDE metadata JSONL text.

        The latest-info endpoint returns JSONL with one record.

        Args:
            session: Reusable HTTP client session.

        Returns:
            Raw JSONL text containing latest build metadata.
        """
        headers = {"User-Agent": self.user_agent}
        url = Template(self.latest_info_url).substitute()
        text, _ = download_text(url=url, headers=headers, session=session)
        return text
