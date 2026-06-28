"""Eve Static Data Package."""

from pathlib import Path

from typer import get_app_dir

__author__ = "Chad Lowe"
__author_email__ = "pfmsoft.dev@gmail.com"
__app_name__ = "Eve Static Data"
__version__ = "0.2.4"
__license__ = "MIT"
__url__ = "https://github.com/DonalChilde/eve-static-data"
__description__ = "A terminal interface for Eve Online Static Data downloading and use."

NAMESPACE = "pfmsoft"
APPLICATION_NAME = "esi-static-data"
DEFAULT_APP_DIR = Path(get_app_dir(f"{NAMESPACE}-{APPLICATION_NAME}"))
USER_AGENT = f"{__app_name__}/{__version__} (+{__url__})"
AFTER_BUILD_NUMBER: int = 3321490
RELEASE_DATE: str = "2026-04-28T11:43:10Z"
SDE_URL_TEMPLATE: str = "https://developers.eveonline.com/static-data/tranquility/eve-online-static-data-${build_number}-${variant}.zip"
DATA_CHANGES_URL_TEMPLATE: str = "https://developers.eveonline.com/static-data/tranquility/changes/${build_number}.jsonl"
SCHEMA_CHANGELOG_URL: str = (
    "https://developers.eveonline.com/static-data/tranquility/schema-changelog.yaml"
)
LATEST_INFO_URL: str = (
    "https://developers.eveonline.com/static-data/tranquility/latest.jsonl"
)
DATA_FILENAME_TEMPLATE: str = "eve-online-static-data-${build_number}-${variant}.zip"
from eve_static_data.sde_tools import SDETools

# TODO decide on the objects to make available as part of the public api.
__all__ = [
    "SDETools",
]
