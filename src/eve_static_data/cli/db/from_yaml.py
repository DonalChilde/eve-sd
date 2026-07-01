# """CLI command to import SDE data from YAML files into the database."""

# import logging
# from pathlib import Path
# from time import perf_counter_ns
# from typing import Annotated

# import typer

# from eve_static_data.db.helpers import create_read_write_connection
# from eve_static_data.db.load_yaml_datasets import import_yaml_sde_to_db
# from eve_static_data.db.models_2 import SerializationFormat
# from eve_static_data.helpers.sde_metadata import load_sde_metadata

# logger = logging.getLogger(__name__)
# app = typer.Typer(no_args_is_help=True)


# @app.command()
# def from_yaml(
#     ctx: typer.Context,
#     sde_yaml_path: Annotated[
#         Path,
#         typer.Argument(
#             help="The path to the SDE data directory containing the YAML files.",
#             exists=True,
#             dir_okay=True,
#         ),
#     ],
#     db_directory: Annotated[
#         Path,
#         typer.Argument(
#             help="The path to the directory that will contain the Sqlite db file.",
#             file_okay=False,
#             dir_okay=True,
#         ),
#     ],
#     db_name: Annotated[
#         str | None,
#         typer.Option(
#             "-n",
#             "--db-name",
#             help="The name of the SQLite database file to create. defaults to None, "
#             "which will create a file named `eve_static_data_{build_number}_yaml.db`",
#             show_default=True,
#         ),
#     ] = None,
#     serialization_format: Annotated[
#         SerializationFormat,
#         typer.Option(
#             "-f",
#             "--serialization-format",
#             help="The serialization format to use for storing records in the database.",
#             case_sensitive=False,
#             show_default=True,
#         ),
#     ] = SerializationFormat.PICKLE,
#     overwrite: Annotated[
#         bool,
#         typer.Option(
#             "-o",
#             "--overwrite",
#             help="Whether to overwrite the database if it already exists.",
#         ),
#     ] = False,
# ):
#     """Import SDE data from YAML files into the database."""
#     sde_metadata = load_sde_metadata(sde_yaml_path)
#     typer.echo(
#         f"Starting import of SDE data from {sde_metadata.variant} files into "
#         f"database at {db_directory} for SDE build {sde_metadata.buildNumber}..."
#     )
#     if db_name is None:
#         db_name = f"eve_static_data_{sde_metadata.buildNumber}_yaml.db"
#     db_path = db_directory / db_name
#     if db_path.exists():
#         if db_path.is_dir():
#             raise IsADirectoryError(f"Database path {db_path} is a directory.")
#         if overwrite:
#             typer.echo(f"Overwriting existing database at {db_path}.")
#             db_path.unlink()
#         else:
#             raise FileExistsError(
#                 f"Database file {db_path} already exists. Use --overwrite to overwrite it."
#             )
#     db_path.parent.mkdir(parents=True, exist_ok=True)
#     connection = create_read_write_connection(str(db_path.resolve()))
#     start_time_ns = perf_counter_ns()
#     import_yaml_sde_to_db(
#         sde_yaml_path, connection=connection, serialization_format=serialization_format
#     )
#     end_time_ns = perf_counter_ns()
#     elapsed_time_s = (end_time_ns - start_time_ns) / 1_000_000_000
#     # Log the time taken to import the data in seconds with 3 decimal places.
#     logger.info(
#         "Finished importing SDE data from %s files into database at %s in %.3f seconds.",
#         sde_metadata.variant,
#         db_path,
#         elapsed_time_s,
#     )

#     typer.echo(
#         f"Finished importing SDE data from {sde_metadata.variant} files into "
#         f"database at {db_path} in {elapsed_time_s:.3f} seconds."
#     )
