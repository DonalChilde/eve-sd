# """Functions for exporting the market paths dataset to a csv file."""

# from collections.abc import Iterable
# from pathlib import Path

# from eve_static_data.exports.helpers import write_dicts_to_csv
# from eve_static_data.models.derived import MarketPathsDataset


# def make_paths_dicts(
#     market_paths: MarketPathsDataset, separator: str = "/"
# ) -> Iterable[dict[str, str | int]]:
#     """Make an iterable of dictionaries containing the market path information.

#     Args:
#         market_paths: The market paths dataset to get the market path information from.
#         separator: The separator to use when converting the market path to a string.

#     Yields:
#         An iterable of dictionaries containing the market path information, with the
#             following keys:
#                 - marketGroupID: The ID of the market group.
#                 - market_path: The market path for the market group as a delimited string.
#                 - market_path_ids: A delimited string of the IDs of the market groups in the market path.
#     """
#     for market_group_id, market_path in market_paths.records.items():
#         yield {
#             "marketGroupID": market_group_id,
#             "market_path": market_path.delimited_str_path(separator=separator),
#             "market_path_ids": market_path.delimited_int_path(separator=separator),
#         }


# def export_market_paths(
#     market_paths: MarketPathsDataset, output_file: Path, overwrite: bool = False
# ) -> int:
#     """Export the market paths dataset to a csv file.

#     Args:
#         market_paths: The market paths dataset to export.
#         output_file: The path to the csv file to write to.
#         overwrite: Whether to overwrite the file if it already exists.

#     Returns:
#         The number of rows written to the csv file.
#     """
#     dicts = make_paths_dicts(market_paths)
#     return write_dicts_to_csv(dicts, output_file, overwrite)
