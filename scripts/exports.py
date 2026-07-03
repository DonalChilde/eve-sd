# /// script
# requires-python = ">=3.13"
# dependencies = []
# ///
import logging
from pathlib import Path
from typing import Annotated

from typer import Typer

from eve_sd import SDELoader
from eve_sd.exports.eve_types_table import export_eve_types_table
from eve_sd.exports.market_paths import export_market_paths
from eve_sd.logging_config import setup_logging

logger = logging.getLogger(__name__)
log_dir = Path("~/tmp/logs/esd-export-script").expanduser()
setup_logging(log_dir=log_dir)
app = Typer(no_args_is_help=True)


@app.command()
def export(sde_path: Annotated[Path, "Path to the SDE directory"]):
    """Export the SDE data to JSON format."""
    derived_path = sde_path / "derived_datasets"
    loader = SDELoader(sde_path=sde_path, derived_datasets_path=derived_path)
    # eve_types_localized = loader.localized_datasets.eve_types()
    # print(f"Exported {len(eve_types_localized.records)} EVE types.")

    market_paths = loader.derived_datasets.market_paths()
    print(f"Exported {len(market_paths.records)} market paths.")
    eve_types = loader.derived_datasets.normalized_eve_types()
    print(f"Exported {len(eve_types.records)} normalized EVE types.")
    region_names = loader.derived_datasets.region_names()
    print(f"Exported {len(region_names.records)} region names.")
    system_names = loader.derived_datasets.system_names()
    print(f"Exported {len(system_names.records)} system names.")

    # -----------------------------------------------------------------
    # After loading the datasets, we can export them to csv files.
    # -----------------------------------------------------------------
    exports_path = sde_path / "exports"

    types_table_filepath = exports_path / "eve_types_table.csv"
    rows_written = export_eve_types_table(
        market_paths=market_paths,
        normalized_eve_types=eve_types,
        output_file=types_table_filepath,
        overwrite=True,
    )
    print(f"Wrote {rows_written} rows to {types_table_filepath}.")

    market_paths_filepath = exports_path / "market_paths.csv"
    rows_written = export_market_paths(
        market_paths=market_paths,
        output_file=market_paths_filepath,
        overwrite=True,
    )
    print(f"Wrote {rows_written} rows to {market_paths_filepath}.")


if __name__ == "__main__":
    app()
    # typer ./scripts/exports.py run ~/tmp/esd/3279491 export
