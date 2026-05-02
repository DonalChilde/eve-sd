"""Functions for loading SDE info from a given input path or SDE zip file."""

import json
import logging
import zipfile
from pathlib import Path
from typing import Any, Literal, TypedDict

logger = logging.getLogger(__name__)


class SdeInfoYaml(TypedDict):
    buildNumber: int
    releaseDate: str


class SdeInfoJsonl(TypedDict):
    _key: str
    buildNumber: int
    releaseDate: str


class SdeDatasetsInfo(TypedDict):
    file_format: Literal["JSONL", "YAML", "JSON"]
    data_format: Literal["JSONL", "YAML"]
    buildNumber: int
    releaseDate: str


# def load_sde_info(input_path: Path) -> SdeInfo:
#     """Get the SDE info from the given input path.

#     The input_path usually points to a directory containing the SDE datasets for a specific
#     build number, and should include a `_sde.jsonl` file with the SDE info. This function
#     reads the first line of the `_sde.jsonl` file, which should contain the SDE info in
#     JSON format, and returns it as an SdeInfo TypedDict.

#     Example of the expected output from the `_sde.jsonl` file:
#     {
#         "_key": "sde",
#         "buildNumber": 123456,
#         "releaseDate": "2024-01-01"
#     }

#     Args:
#         input_path: The path to the directory containing the SDE datasets and the `_sde.jsonl` file.

#     Returns:
#         An SdeInfo TypedDict containing the SDE info from the `_sde.jsonl` file.

#     Raises:
#         FileNotFoundError: If the `_sde.jsonl` file is not found at the given input path.
#         json.JSONDecodeError: If the first line of the `_sde.jsonl` file is not valid JSON.
#         KeyError: If the expected keys are not found in the JSON data.
#     """
#     sde_info_path = input_path / "_sde.jsonl"
#     if not sde_info_path.exists():
#         raise FileNotFoundError(f"_sde.jsonl file not found at {input_path}.")
#     with open(sde_info_path) as f:
#         first_line = f.readline()
#         sde_info = json.loads(first_line)
#     return SdeInfo(**sde_info)


# def load_sde_info_from_zipfile(sde_zip_file: Path) -> SdeInfo:
#     """Get the SDE info from the given SDE zip file.

#     This function opens the given SDE zip file, looks for the `_sde.jsonl` file inside it,
#     reads the first line of that file, which should contain the SDE info in JSON format, and
#     returns it as an SdeInfo TypedDict.

#     Args:
#         sde_zip_file: The path to the SDE zip file.

#     Returns:
#         An SdeInfo TypedDict containing the SDE info from the `_sde.jsonl` file inside the zip file.

#     Raises:
#         FileNotFoundError: If the `_sde.jsonl` file is not found inside the zip file.
#         json.JSONDecodeError: If the first line of the `_sde.jsonl` file is not valid JSON.
#         KeyError: If the expected keys are not found in the JSON data.
#     """
#     with zipfile.ZipFile(sde_zip_file, "r") as zip_ref:
#         with zip_ref.open("_sde.jsonl") as f:
#             first_line = f.readline().decode("utf-8")
#             sde_info = json.loads(first_line)
#     return SdeInfo(**sde_info)


def detect_sde_info_file(input_path: Path) -> Path | None:
    """Detect the path to the SDE info file (_sde.*) given an input path.

    The suffix can be .yaml, .yml, json, or jsonl. The function checks for the existence
    of these files in the input path. If none of these files are found, it returns None.

    If more than one is found, it raises a ValueError.
    """
    if not input_path.is_dir():
        raise NotADirectoryError(f"Input path {input_path} is not a directory.")
    possible_suffixes = [".yaml", ".yml", ".json", ".jsonl"]
    found_files: list[Path] = []
    for suffix in possible_suffixes:
        candidate_file = input_path / f"_sde{suffix}"
        if candidate_file.exists() and candidate_file.is_file():
            found_files.append(candidate_file)
    if len(found_files) > 1:
        raise ValueError(
            f"Multiple SDE info files found in {input_path}: {found_files}"
        )
    elif len(found_files) == 0:
        return None
    else:
        return found_files[0]


def detect_sde_info_file_in_zipfile(sde_zip_file: Path) -> str | None:
    """Detect the name of the SDE info file (_sde.*) inside the given SDE zip file.

    The suffix can be .yaml, .yml, json, or jsonl. The function checks for the existence
    of these files inside the zip file. If none of these files are found, it returns None.

    If more than one is found, it raises a ValueError.
    """
    # Note, the SDE zipfiles are flat, so we don't need to worry about searching through
    # subdirectories in the zip file. We can just check the root level of the zip file
    # for the presence of any of the expected SDE info files.
    possible_suffixes = [".yaml", ".yml", ".json", ".jsonl"]
    found_files: list[str] = []
    with zipfile.ZipFile(sde_zip_file, "r") as zip_ref:
        for suffix in possible_suffixes:
            candidate_file = f"_sde{suffix}"
            if candidate_file in zip_ref.namelist():
                found_files.append(candidate_file)
    if len(found_files) > 1:
        raise ValueError(
            f"Multiple SDE info files found in {sde_zip_file}: {found_files}"
        )
    elif len(found_files) == 0:
        return None
    else:
        return found_files[0]


def sde_info_from_dict(
    sde_info_dict: dict[str, Any], file_format: Literal["JSONL", "YAML", "JSON"]
) -> SdeDatasetsInfo:
    """Helper function to convert a dict containing SDE info into an SdeInfo TypedDict."""
    if "_key" in sde_info_dict:
        # This is the JSONL format
        # check for the expected keys for JSONL format
        if "buildNumber" not in sde_info_dict or "releaseDate" not in sde_info_dict:
            raise KeyError(
                "Expected 'buildNumber' and 'releaseDate' keys in SDE info dict for JSONL format."
            )
        return SdeDatasetsInfo(
            file_format=file_format,
            data_format="JSONL",
            buildNumber=int(sde_info_dict["buildNumber"]),
            releaseDate=str(sde_info_dict["releaseDate"]),
        )

    if "sde" in sde_info_dict:
        # This is the YAML format
        yaml_sde_dict: SdeInfoYaml = sde_info_dict["sde"]
        if "buildNumber" not in yaml_sde_dict or "releaseDate" not in yaml_sde_dict:
            raise KeyError(
                "Expected 'buildNumber' and 'releaseDate' keys in 'sde' section of SDE info dict for YAML format."
            )
        return SdeDatasetsInfo(
            file_format=file_format,
            data_format="YAML",
            buildNumber=int(yaml_sde_dict["buildNumber"]),
            releaseDate=str(yaml_sde_dict["releaseDate"]),
        )
    logger.error(
        "SDE info dict does not contain expected keys for either JSONL or YAML format: %s",
        sde_info_dict,
    )
    raise ValueError(
        "SDE info dict does not contain expected keys for either JSONL or YAML format."
    )


def load_sde_info_from_detected_file(sde_directory: Path) -> SdeDatasetsInfo:
    """Load the SDE info from the detected SDE info file in the given directory.

    This function first detects the SDE info file using `detect_sde_info_file`, then loads
    the SDE info from that file. It currently supports YAML, JSONL, and the json formats of both.

    Args:
        sde_directory: The path to the directory containing the SDE info file.

    Returns:
        An SdeInfo TypedDict containing the SDE info from the detected SDE info file.

    Raises:
        FileNotFoundError: If no SDE info file is found in the given directory.
        ValueError: If the detected SDE info file has an unsupported format.
        json.JSONDecodeError: If the content of the detected SDE info file is not valid JSON (for JSONL or JSON formats).
        KeyError: If the expected keys are not found in the loaded data from the detected SDE info file.
    """
    sde_info_file = detect_sde_info_file(sde_directory)
    if sde_info_file is None:
        raise FileNotFoundError(f"No SDE info file found in {sde_directory}.")
    if sde_info_file.suffix in [".yaml", ".yml"]:
        import yaml

        with open(sde_info_file) as f:
            loaded_data: dict[str, Any] = yaml.safe_load(f)
            file_format = "YAML"
    elif sde_info_file.suffix in [".jsonl"]:
        with open(sde_info_file) as f:
            first_line = f.readline()
            loaded_data: dict[str, Any] = json.loads(first_line)
            file_format = "JSONL"
    elif sde_info_file.suffix == ".json":
        with open(sde_info_file) as f:
            loaded_data: dict[str, Any] = json.load(f)
            file_format = "JSON"
    else:
        raise ValueError(f"Unsupported SDE info file format: {sde_info_file.suffix}")

    return sde_info_from_dict(loaded_data, file_format=file_format)


def load_sde_info_from_detected_file_in_zipfile(sde_zip_file: Path) -> SdeDatasetsInfo:
    """Load the SDE info from the detected SDE info file inside the given SDE zip file.

    This function first detects the SDE info file using `detect_sde_info_file_in_zipfile`, then loads
    the SDE info from that file. It currently supports YAML, JSONL, and the json formats of both.

    Args:
        sde_zip_file: The path to the SDE zip file.

    Returns:
        An SdeInfo TypedDict containing the SDE info from the detected SDE info file inside the zip file.

    Raises:
        FileNotFoundError: If no SDE info file is found in the given SDE zip file.
        ValueError: If the detected SDE info file has an unsupported format.
        json.JSONDecodeError: If the content of the detected SDE info file is not valid JSON (for JSONL or JSON formats).
        KeyError: If the expected keys are not found in the loaded data from the detected SDE info file.
    """
    sde_info_file = detect_sde_info_file_in_zipfile(sde_zip_file)
    if sde_info_file is None:
        raise FileNotFoundError(f"No SDE info file found in {sde_zip_file}.")
    with zipfile.ZipFile(sde_zip_file, "r") as zip_ref:
        with zip_ref.open(sde_info_file) as f:
            if sde_info_file.endswith((".yaml", ".yml")):
                import yaml

                loaded_data: dict[str, Any] = yaml.safe_load(f)
                file_format = "YAML"
            elif sde_info_file.endswith(".jsonl"):
                first_line = f.readline().decode("utf-8")
                loaded_data: dict[str, Any] = json.loads(first_line)
                file_format = "JSONL"
            elif sde_info_file.endswith(".json"):
                loaded_data: dict[str, Any] = json.load(f)
                file_format = "JSON"
            else:
                raise ValueError(
                    f"Unsupported SDE info file format in zip file: {sde_info_file}"
                )
    return sde_info_from_dict(loaded_data, file_format=file_format)
