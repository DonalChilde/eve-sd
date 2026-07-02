"""Application settings for eve-static-data.

This module defines two settings models:
- ``EveStaticDataSettingsPydantic`` for loading values from environment variables
    and optional ``.env`` files.
- ``EveStaticDataSettings`` as the runtime dataclass used by the app.
"""

from dataclasses import dataclass
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from eve_static_data import (
    DATA_CHANGES_URL_TEMPLATE,
    DATA_FILENAME_TEMPLATE,
    DEFAULT_APP_DIR,
    LATEST_INFO_URL,
    SCHEMA_CHANGELOG_URL,
    SDE_URL_TEMPLATE,
)

_app_env_prefix = "PFMSOFT_EVE_STATIC_DATA_"


@dataclass(slots=True)
class EveStaticDataSettings:
    """Runtime settings consumed by eve-static-data components."""

    application_directory: Path
    logging_directory: Path
    # sde_directory: Path
    sde_latest_info_url: str = LATEST_INFO_URL
    sde_download_url_template: str = SDE_URL_TEMPLATE
    sde_data_changes_url_template: str = DATA_CHANGES_URL_TEMPLATE
    sde_schema_changelog_url: str = SCHEMA_CHANGELOG_URL
    sde_data_filename_template: str = DATA_FILENAME_TEMPLATE


class EveStaticDataSettingsPydantic(BaseSettings):
    """Settings for Eve Static Data application.

    This model is the source of truth for configuration loading. Values are
    read from environment variables prefixed with ``PFMSOFT_EVE_STATIC_DATA_``
    and from ``.eve-static-data.env`` when present.

    ``get_settings()`` converts this model into the runtime
    ``EveStaticDataSettings`` dataclass.
    """

    model_config = SettingsConfigDict(
        env_prefix=_app_env_prefix,
        env_file=".eve-static-data.env",
        env_file_encoding="utf-8",
    )

    application_directory: Path = Field(
        default=DEFAULT_APP_DIR,
        description="The application directory path.",
    )
    logging_directory: Path = Field(
        default=DEFAULT_APP_DIR / "logs",
        description="The directory where log files are stored.",
    )
    sde_latest_info_url: str = Field(
        default=LATEST_INFO_URL,
        description="The URL to get information about the latest SDE data.",
    )
    sde_download_url_template: str = Field(
        default=SDE_URL_TEMPLATE,
        description="The URL template to download the SDE data file. build-number can be any valid build number. variant can be jsonl or yaml",
    )
    sde_data_changes_url_template: str = Field(
        default=DATA_CHANGES_URL_TEMPLATE,
        description="The URL template to download the SDE changes file. build-number can be any valid build number.",
    )
    sde_schema_changelog_url: str = Field(
        default=SCHEMA_CHANGELOG_URL,
        description="The URL to get the SDE schema changelog.",
    )
    sde_data_filename_template: str = Field(
        default=DATA_FILENAME_TEMPLATE,
        description="The filename template for the SDE data file. build-number can be any valid build number. variant can be jsonl or yaml",
    )


def get_settings(
    pydantic_settings: EveStaticDataSettingsPydantic | None = None,
) -> EveStaticDataSettings:
    """Build runtime settings from a Pydantic settings model.

    Args:
        pydantic_settings: Optional prebuilt Pydantic settings model. When
            omitted, a new instance is created using configured env sources.

    Returns:
        Runtime settings dataclass used by the application.

    Notes:
        This function ensures the application and logging directories exist.
    """
    if pydantic_settings is None:
        pydantic_settings = EveStaticDataSettingsPydantic()
    settings = EveStaticDataSettings(
        application_directory=pydantic_settings.application_directory,
        logging_directory=pydantic_settings.logging_directory,
        sde_latest_info_url=pydantic_settings.sde_latest_info_url,
        sde_download_url_template=pydantic_settings.sde_download_url_template,
        sde_data_changes_url_template=pydantic_settings.sde_data_changes_url_template,
        sde_schema_changelog_url=pydantic_settings.sde_schema_changelog_url,
        sde_data_filename_template=pydantic_settings.sde_data_filename_template,
    )
    # Ensure that the application directories exist.
    settings.application_directory.mkdir(parents=True, exist_ok=True)
    settings.logging_directory.mkdir(parents=True, exist_ok=True)
    return settings
