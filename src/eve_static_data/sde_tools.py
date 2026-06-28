"""Implementation of the EsdTools."""

# TODO This could be refactored to be just functions in a package instead of a class, since it doesn't really need to maintain state.

from pathlib import Path
from string import Template

from httpx2 import Client

from eve_static_data import (
    DATA_CHANGES_URL_TEMPLATE,
    DATA_FILENAME_TEMPLATE,
    LATEST_INFO_URL,
    SCHEMA_CHANGELOG_URL,
    SDE_URL_TEMPLATE,
    USER_AGENT,
)
from eve_static_data.helpers.httpx2.download_files import (
    download_bytes_to_file,
    download_text,
)
from eve_static_data.helpers.sde_metadata import SdeMetadata
from eve_static_data.helpers.sde_unpack import unpack as unpack_sde


class SDETools:
    """Class for handling SDE tools static data."""

    def __init__(
        self,
        latest_info_url: str = LATEST_INFO_URL,
        download_url_template: str = SDE_URL_TEMPLATE,
        data_changes_url_template: str = DATA_CHANGES_URL_TEMPLATE,
        schema_changelog_url: str = SCHEMA_CHANGELOG_URL,
        data_filename_template: str = DATA_FILENAME_TEMPLATE,
        user_agent: str = USER_AGENT,
    ):
        """The SDETools class for handling EVE Static Data."""
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
        """Download the SDE tools static data."""
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
        """Unpack the downloaded static data."""
        file_path, info = unpack_sde(
            input_path, output_path, use_build_number=use_build_number
        )
        return file_path, info

    def validate(self, sde_path: Path, report_directory: Path) -> None:
        """Validate the SDE tools static data."""
        raise NotImplementedError("SDE validation is not yet implemented.")

    def fetch_data_changes(self, build_number: int, *, session: Client) -> str:
        """Download the sde data changes for the given build number.

        The SDE data changes is a JSONL file that contains a list of changes for a build.
        The record with key _meta contains lastBuildNumber, referring to the previous SDE.

        Each line can be parsed with json.loads to convert the JSONL text into a Python dictionary.
        """
        headers = {"User-Agent": self.user_agent}
        url = Template(self.data_changes_url_template).substitute(
            build_number=build_number
        )
        text, _ = download_text(url=url, headers=headers, session=session)
        return text

    def fetch_schema_changelog(self, build_number: int, *, session: Client) -> str:
        """Download the sde schema changelog for the given build number.

        The SDE schema changelog is a YAML file that contains a list of schema changes for a build.
        This function returns the raw YAML text of the changelog. use safe_load from the
        yaml library to parse the YAML text into a Python dictionary.
        """
        headers = {"User-Agent": self.user_agent}
        url = Template(self.schema_changelog_url).substitute(build_number=build_number)
        text, _ = download_text(url=url, headers=headers, session=session)
        return text

    def fetch_latest_sde_info(self, *, session: Client) -> str:
        """Download the latest sde info.

        The latest sde info is a JSONL file that contains information about the latest
        SDE build, including the latest build number and release date.

        Because the latest sde info is a JSONL file with a single record, this function
        returns the raw JSONL text of the latest sde info. use json.loads to parse the
        JSONL text into a Python dictionary.
        """
        headers = {"User-Agent": self.user_agent}
        url = Template(self.latest_info_url).substitute()
        text, _ = download_text(url=url, headers=headers, session=session)
        return text
