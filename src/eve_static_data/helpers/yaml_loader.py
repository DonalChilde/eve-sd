"""Helper functions for loading YAML files."""

import logging
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)
try:
    from yaml import CSafeLoader as SafeLoader

    logger.info("Using CSafeLoader for YAML parsing.")
except ImportError:
    from yaml import SafeLoader

    logger.info("CSafeLoader not available, using SafeLoader for YAML parsing.")


def safe_load_path(file_path: Path) -> Any:
    """Safely load a YAML file and return the resulting Python object.

    If the CSafeLoader is available, it will be used for improved performance.
    Otherwise, the SafeLoader will be used.

    Args:
        file_path: The path to the YAML file to load.

    Returns:
        The Python object resulting from parsing the YAML file.

    Raises:
        yaml.YAMLError: If there is an error parsing the YAML file.
        FileNotFoundError: If the specified file does not exist.
    """
    with file_path.open() as f:
        loaded_object = yaml.load(f, Loader=SafeLoader)
    return loaded_object


def safe_load_IO(file_io: Any) -> Any:
    """Safely load YAML content from a file-like object and return the resulting Python object.

    If the CSafeLoader is available, it will be used for improved performance.
    Otherwise, the SafeLoader will be used.

    Args:
        file_io: A file-like object containing YAML content to load.

    Returns:
        The Python object resulting from parsing the YAML content.

    Raises:
        yaml.YAMLError: If there is an error parsing the YAML content.
    """
    loaded_object = yaml.load(file_io, Loader=SafeLoader)
    return loaded_object
