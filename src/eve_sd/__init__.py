"""Eve SD Package."""

from pathlib import Path
from typing import Any

from typer import get_app_dir

__author__ = "Chad Lowe"
__author_email__ = "pfmsoft.dev@gmail.com"
__app_name__ = "Eve SD"
__version__ = "0.4.0"
__license__ = "MIT"
__url__ = "https://github.com/DonalChilde/eve-sd"
__description__ = "A terminal interface for Eve Online Static Data downloading and use."

NAMESPACE = "pfmsoft"
APPLICATION_NAME = "eve-sd"
DEFAULT_APP_DIR = Path(get_app_dir(f"{NAMESPACE}-{APPLICATION_NAME}"))
USER_AGENT = f"{__app_name__}/{__version__} (+{__url__})"

SDE_URL_TEMPLATE: str = "https://developers.eveonline.com/static-data/tranquility/eve-online-static-data-${build_number}-${variant}.zip"
DATA_CHANGES_URL_TEMPLATE: str = "https://developers.eveonline.com/static-data/tranquility/changes/${build_number}.jsonl"
SCHEMA_CHANGELOG_URL: str = (
    "https://developers.eveonline.com/static-data/tranquility/schema-changelog.yaml"
)
LATEST_INFO_URL: str = (
    "https://developers.eveonline.com/static-data/tranquility/latest.jsonl"
)
DATA_FILENAME_TEMPLATE: str = "eve-online-static-data-${build_number}-${variant}.zip"

type Record = dict[str | int, Any]
"""Type alias for a record from an EVE SDE dataset."""
type IntKeyedRecord = tuple[int, Record]
"""Type alias for a record from an EVE SDE dataset with an integer key."""
type StrKeyedRecord = tuple[str, Record]
"""Type alias for a record from an EVE SDE dataset with a string key."""
type KeyedRecord = IntKeyedRecord | StrKeyedRecord
"""Type alias for a record from an EVE SDE dataset with either an integer or string key."""
type Dataset = dict[str | int, Record]
"""Type alias for an EVE SDE dataset, which is a mapping of keys to records."""
from eve_sd.db.helpers import create_read_write_connection
from eve_sd.db.query import DatasetDbQuery
from eve_sd.sde_tools import SDETools

__all__ = [
    "SDETools",
    "create_read_write_connection",
    "DatasetDbQuery",
]
