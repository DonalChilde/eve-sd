# """Helper functions for working with app data directories and URLs."""

# from pathlib import Path
# from string import Template
# from typing import Literal


# def sde_download_url(
#     url_template_str: str, build_number: int, variant: Literal["jsonl", "yaml"]
# ) -> str:
#     """Resolve the SDE download URL for a specific build number and variant."""
#     url_template = Template(url_template_str)
#     url = url_template.substitute(variant=variant, build_number=build_number)
#     return url


# def sde_changes_url(url_template_str: str, build_number: int) -> str:
#     """Resolve the URL to get the SDE changes for a specific build number."""
#     url_template = Template(url_template_str)
#     url = url_template.substitute(build_number=build_number)
#     return url


# def sde_data_filename(
#     filename_template_str: str, build_number: int, variant: Literal["jsonl", "yaml"]
# ) -> str:
#     """Resolve the filename for the SDE data file for a specific build number and variant."""
#     filename_template = Template(filename_template_str)
#     filename = filename_template.substitute(variant=variant, build_number=build_number)
#     return filename


# def available_builds(data_path: Path) -> list[int]:
#     """Get a sorted list of available build numbers."""
#     builds: list[int] = []
#     for build_dir in data_path.iterdir():
#         if build_dir.is_dir() and build_dir.name.isdigit():
#             builds.append(int(build_dir.name))
#     return sorted(builds)


# def latest_build(data_path: Path) -> int:
#     """Get the latest available build number, or None if no builds are available."""
#     builds = available_builds(data_path)
#     if not builds:
#         raise ValueError(f"No available builds found in data directory {data_path}")
#     return builds[-1]


# # def build_data_dir(
# #     data_path: Path, build_number: int, initialize: bool = False
# # ) -> Path:
# #     """Get the directory path for a specific build number."""
# #     build_dir = data_path / str(build_number)
# #     if initialize:
# #         if build_dir.exists():
# #             raise FileExistsError(
# #                 f"Tried to initialize build data directory, but it already exists: {build_dir}"
# #             )
# #         build_dir.mkdir(parents=True, exist_ok=False)
# #         build_data_sde_dir(build_dir).mkdir(parents=True, exist_ok=False)
# #         build_data_derived_dir(build_dir).mkdir(parents=True, exist_ok=False)
# #         build_data_validation_dir(build_dir).mkdir(parents=True, exist_ok=False)

# #     return build_dir


# def sde_top_dir(data_path: Path, build_number: int) -> Path:
#     """Get the top directory path for the SDE data of a specific build number."""
#     top_dir = data_path / str(build_number)
#     return top_dir


# def sde_dir(data_path: Path, build_number: int) -> Path:
#     """Get the directory path for the SDE data within the top directory."""
#     top_dir = sde_top_dir(data_path, build_number)
#     sde_dir = top_dir / "sde"
#     return sde_dir


# def derived_dir(data_path: Path, build_number: int) -> Path:
#     """Get the directory path for the derived data within the top directory."""
#     top_dir = sde_top_dir(data_path, build_number)
#     derived_dir = top_dir / "derived"
#     return derived_dir


# def validation_dir(data_path: Path, build_number: int) -> Path:
#     """Get the directory path for the validation data within the top directory."""
#     top_dir = sde_top_dir(data_path, build_number)
#     validation_dir = top_dir / "validation"
#     return validation_dir


# def init_dirs(data_path: Path, build_number: int):
#     """Initialize the directory structure for a specific build number."""
#     sde_top_dir(data_path, build_number).mkdir(parents=True, exist_ok=True)
#     sde_dir(data_path, build_number).mkdir(parents=True, exist_ok=True)
#     derived_dir(data_path, build_number).mkdir(parents=True, exist_ok=True)
#     validation_dir(data_path, build_number).mkdir(parents=True, exist_ok=True)
