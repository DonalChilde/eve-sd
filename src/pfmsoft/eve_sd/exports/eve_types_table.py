# """Functions for exporting the eve types table to a csv file."""

# from collections.abc import Iterable
# from pathlib import Path
# from typing import Any

# from eve_static_data.exports.helpers import write_dicts_to_csv
# from eve_static_data.models.derived import MarketPathsDataset, NormalizedEveTypesDataset
# from eve_static_data.models.derived.normalized_eve_type import NormalizedEveType


# def export_eve_types_table(
#     market_paths: MarketPathsDataset,
#     normalized_eve_types: NormalizedEveTypesDataset,
#     output_file: Path,
#     overwrite: bool = False,
# ) -> int:
#     """Export a table of eve types with their market paths to a csv file.

#     Args:
#         market_paths: The market paths dataset to get the market paths from.
#         normalized_eve_types: The normalized eve types dataset to get the eve type information from.
#         output_file: The path to the csv file to write to.
#         overwrite: Whether to overwrite the file if it already exists.

#     Returns:
#         The number of rows written to the csv file.
#     """
#     output_dicts = add_market_path(market_paths, normalized_eve_types.records.values())
#     return write_dicts_to_csv(output_dicts, output_file, overwrite)


# def add_market_path(
#     market_paths: MarketPathsDataset, normalized_eve_types: Iterable[NormalizedEveType]
# ) -> Iterable[dict[str, Any]]:
#     """Add market path information to the normalized eve types dataset records.

#     Changes the Eve type records to dictionaries and adds a "market_path" key to each
#     dictionary, with the value being the market path for that eve type if it exists, or
#     an empty string if it does not.

#     Args:
#         market_paths: The market paths dataset to get the market paths from.
#         normalized_eve_types: The normalized eve types dataset to add the market path
#             information to.

#     Yields:
#         An iterable of dictionaries containing the eve type information with market path
#             information added.
#     """
#     for eve_type in normalized_eve_types:
#         dict_obj = eve_type.model_dump(mode="json")
#         if eve_type.marketGroupID is not None:
#             market_path = market_paths.records.get(eve_type.marketGroupID)
#             dict_obj["market_path"] = (
#                 market_path.delimited_str_path() if market_path is not None else ""
#             )
#         yield dict_obj
