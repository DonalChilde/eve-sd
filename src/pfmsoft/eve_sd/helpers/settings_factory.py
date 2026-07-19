"""Helper functions to create objects from Settings."""

from pfmsoft.eve_sd.sde_tools import SDETools
from pfmsoft.eve_sd.settings import EveSDSettings


def sde_tools_factory(settings: EveSDSettings) -> SDETools:
    """Factory function to create an instance of SDETools."""
    return SDETools(
        latest_info_url=settings.sde_latest_info_url,
        download_url_template=settings.sde_download_url_template,
        data_changes_url_template=settings.sde_data_changes_url_template,
        schema_changelog_url=settings.sde_schema_changelog_url,
        data_filename_template=settings.sde_data_filename_template,
    )
