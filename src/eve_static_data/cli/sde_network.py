# """SDE raw data CLI commands for esi-link.

# This module focuses on commands to work with the raw SDE data, such as downloading,
# checking for the current version, checking the changelog, and printing the data.
# """

# import json
# from pathlib import Path
# from typing import Annotated, Literal

# import typer
# from rich.console import Console

# from eve_static_data.cli.helpers import get_esd_settings_from_context
# from eve_static_data.helpers.http_client import config_http_client

# app = typer.Typer(no_args_is_help=True)


# @app.command()
# def latest(
#     ctx: typer.Context,
#     file_out: Annotated[
#         Path | None,
#         typer.Option(
#             "--file-out",
#             help="The file to save the latest SDE information to a json file.",
#             file_okay=True,
#         ),
#     ] = None,
#     terminal: Annotated[
#         bool,
#         typer.Option(
#             "--terminal",
#             help="Whether to print the latest SDE information to the terminal.",
#             show_default=True,
#         ),
#     ] = False,
# ):
#     """Fetch and show information about the latest available SDE data."""
#     console = Console()
#     if not file_out and not terminal:
#         console.print(
#             "[bold red]Error:[/bold red] No output method specified. Please provide a file path or enable terminal output."
#         )
#         raise typer.Exit(code=1)
#     console.print("[bold green]Latest SDE Information[/bold green]")
#     settings = get_esd_settings_from_context(ctx)
#     sde_tools = settings.sde_tools()
#     session = config_http_client()
#     info = sde_tools.fetch_latest_sde_info(session=session)
#     if terminal:
#         console.print(info)
#     if file_out:
#         try:
#             with file_out.open("w", encoding="utf-8") as f:
#                 f.write(str(info))
#             console.print(f"Latest SDE information saved to {file_out}")
#         except Exception as e:
#             console.print(
#                 f"[bold red]Error:[/bold red] Failed to save latest SDE information to file: {e}"
#             )
#             raise typer.Exit(code=1) from e


# @app.command()
# def schema_changelog(
#     ctx: typer.Context,
#     build_number: Annotated[
#         int | None,
#         typer.Option(
#             help="The build number of the SDE schema changelog to fetch. If not provided, the changelog for the latest build will be fetched.",
#         ),
#     ] = None,
#     file_out: Annotated[
#         Path | None,
#         typer.Option(
#             "--file-out",
#             help="The file to save the SDE schema changelog information to a yaml file.",
#             file_okay=True,
#         ),
#     ] = None,
#     terminal: Annotated[
#         bool,
#         typer.Option(
#             "--terminal",
#             help="Whether to print the SDE schema changelog information to the terminal.",
#             show_default=True,
#         ),
#     ] = False,
# ):
#     """Fetch and show the changelog for the SDE schema."""
#     console = Console()
#     if not file_out and not terminal:
#         console.print(
#             "[bold red]Error:[/bold red] No output method specified. Please provide a file path or enable terminal output."
#         )
#         raise typer.Exit(code=1)
#     console.print("[bold green]SDE Schema Changelog[/bold green]")
#     settings = get_esd_settings_from_context(ctx)
#     session = config_http_client()
#     sde_tools = settings.sde_tools()
#     if build_number is None:
#         console.print("No build number provided, resolving latest build number...")
#         latest_info = sde_tools.fetch_latest_sde_info(session=session)
#         latest_info = json.loads(latest_info)
#         build_number = latest_info.get("buildNumber")
#         if not build_number:
#             console.print(
#                 "[bold red]Error:[/bold red] Could not resolve latest build number."
#             )
#             console.print(latest_info)
#             raise typer.Exit(code=1)
#         console.print(f"Resolved latest build number to: {build_number}")
#     changelog = sde_tools.fetch_schema_changelog(
#         build_number=build_number, session=session
#     )
#     if terminal:
#         console.print(changelog)
#     if file_out:
#         try:
#             with file_out.open("w", encoding="utf-8") as f:
#                 f.write(changelog)
#             console.print(f"SDE schema changelog saved to {file_out}")
#         except Exception as e:
#             console.print(
#                 f"[bold red]Error:[/bold red] Failed to save SDE schema changelog to file: {e}"
#             )
#             raise typer.Exit(code=1) from e


# @app.command()
# def data_changelog(
#     ctx: typer.Context,
#     build_number: Annotated[
#         int | None,
#         typer.Option(
#             help="The build number of the SDE data to show the changelog for. If not "
#             "provided, the changelog for the latest build will be shown."
#         ),
#     ] = None,
#     file_out: Annotated[
#         Path | None,
#         typer.Option(
#             "--file-out",
#             help="The file to save the SDE data changelog information to a jsonl file.",
#             file_okay=True,
#         ),
#     ] = None,
#     terminal: Annotated[
#         bool,
#         typer.Option(
#             "--terminal",
#             help="Whether to print the SDE data changelog information to the terminal.",
#             show_default=True,
#         ),
#     ] = False,
# ):
#     """Fetch and show the changelog for the SDE data.

#     Note the changelog for the SDE data is different from the changelog for the SDE schema.
#     The SDE data changelog tracks changes in the actual data, while the SDE schema changelog
#     tracks changes in the structure of the data.

#     The data changelog is in JSONL format, where each line is a JSON object representing
#     a change in the SDE data.
#     """
#     console = Console()
#     if not file_out and not terminal:
#         console.print(
#             "[bold red]Error:[/bold red] No output method specified. Please provide a file path or enable terminal output."
#         )
#         raise typer.Exit(code=1)
#     console.print("[bold green]SDE Data Changelog[/bold green]")
#     settings = get_esd_settings_from_context(ctx)
#     session = config_http_client()
#     sde_tools = settings.sde_tools()
#     if build_number is None:
#         console.print("No build number provided, resolving latest build number...")
#         latest_info = sde_tools.fetch_latest_sde_info(session=session)
#         latest_info = json.loads(latest_info)
#         build_number = latest_info.get("buildNumber")
#         if not build_number:
#             console.print(
#                 "[bold red]Error:[/bold red] Could not resolve latest build number."
#             )
#             console.print(latest_info)
#             raise typer.Exit(code=1)
#         console.print(f"Resolved latest build number to: {build_number}")
#     changelog = sde_tools.fetch_data_changes(build_number=build_number, session=session)
#     if terminal:
#         console.print(changelog)
#     if file_out:
#         try:
#             with file_out.open("w", encoding="utf-8") as f:
#                 f.write(str(changelog))
#             console.print(f"SDE data changelog saved to {file_out}")
#         except Exception as e:
#             console.print(
#                 f"[bold red]Error:[/bold red] Failed to save SDE data changelog to file: {e}"
#             )
#             raise typer.Exit(code=1) from e


# @app.command(name="download")
# def download_sde(
#     ctx: typer.Context,
#     output_dir: Annotated[
#         Path,
#         typer.Argument(
#             help="The directory to save the downloaded SDE data. The file name will "
#             "be automatically generated.",
#             file_okay=False,
#         ),
#     ],
#     variant: Annotated[
#         Literal["jsonl", "yaml"],
#         typer.Option(
#             "--variant",
#             help="The variant of the SDE to download",
#             show_default=True,
#         ),
#     ] = "yaml",
#     build_number: Annotated[
#         int | None,
#         typer.Option(
#             "--build-number",
#             help="The build number of the SDE to download. If not provided, the latest "
#             "build will be downloaded.",
#             show_default=True,
#         ),
#     ] = None,  # None will be resolved to latest build number
#     overwrite: Annotated[
#         bool,
#         typer.Option(
#             "--overwrite", help="Whether to overwrite existing files", show_default=True
#         ),
#     ] = False,
# ):
#     """Download the latest SDE data."""
#     console = Console()
#     console.print("[bold green]Downloading SDE Data...[/bold green]")
#     settings = get_esd_settings_from_context(ctx)
#     session = config_http_client()
#     sde_tools = settings.sde_tools()
#     if build_number is None:
#         console.print("No build number provided, resolving latest build number...")
#         latest_info = sde_tools.fetch_latest_sde_info(session=session)
#         latest_info = json.loads(latest_info)
#         build_number = latest_info.get("buildNumber")
#         release_date = latest_info.get("releaseDate")
#         if not build_number:
#             console.print(
#                 "[bold red]Error:[/bold red] Could not resolve latest build number."
#             )
#             console.print(latest_info)
#             raise typer.Exit(code=1)
#         console.print(
#             f"Resolved latest build number to: {build_number}, released on {release_date}"
#         )

#     console.print(f"Downloading SDE data, {variant} variant.")

#     try:
#         file_path = sde_tools.download(
#             build_number=build_number,
#             output_directory=output_dir,
#             variant=variant,
#             overwrite=overwrite,
#             session=session,
#         )

#     except Exception as e:
#         console.print(f"[bold red]Error:[/bold red] Failed to download SDE data: {e}")
#         raise typer.Exit(code=1) from e

#     console.print(
#         f"SDE data, {variant} variant downloaded successfully, saved to: {file_path}"
#     )
