"""Helpers for working with unpacked SDE directories."""

from pathlib import Path

from eve_static_data.helpers.sde_info import (
    SdeDatasetsInfo,
    detect_sde_info_file,
    load_sde_info_from_detected_file,
)


def is_sde_directory(path: Path) -> bool:
    """Return ``True`` if the provided path appears to be an SDE data directory.

    Args:
        path: Candidate directory path.

    Returns:
        ``True`` when the directory contains exactly one supported ``_sde.*`` file.
    """
    try:
        return detect_sde_info_file(path) is not None
    except (NotADirectoryError, ValueError):
        return False


def load_sde_info(path: Path) -> SdeDatasetsInfo:
    """Load normalized SDE metadata from an unpacked SDE directory.

    Args:
        path: Directory containing SDE dataset files and an ``_sde.*`` file.

    Returns:
        Normalized metadata dictionary containing file format, data format,
        build number, and release date.
    """
    return load_sde_info_from_detected_file(path)
