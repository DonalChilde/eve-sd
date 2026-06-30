"""Helper functions for loading and dumping YAML files.

Will use the C-based SafeLoader and SafeDumper if available for improved performance,
otherwise will fall back to the pure Python implementations.
"""

import logging
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)
try:
    from yaml import CSafeDumper as SafeDumper
    from yaml import CSafeLoader as SafeLoader

    logger.info("Using CSafeLoader and CSafeDumper for YAML parsing.")
except ImportError:
    from yaml import SafeDumper, SafeLoader

    logger.info(
        "CSafeLoader or CSafeDumper not available, using SafeLoader and SafeDumper for YAML parsing."
    )


def safe_dump_path(data: Any, file_path: Path, **kwargs: Any) -> None:
    """Safely dump a Python object to a YAML file.

    If the CSafeDumper is available, it will be used for improved performance.
    Otherwise, the SafeDumper will be used.

    Args:
        data: The Python object to dump to YAML.
        file_path: The path to the YAML file to write.
        **kwargs: Additional keyword arguments to pass to yaml.dump.

    Raises:
        yaml.YAMLError: If there is an error dumping the YAML file.
    """
    with file_path.open("w") as f:
        yaml.dump(data, f, Dumper=SafeDumper, **kwargs)


def safe_dump_IO(data: Any, file_io: Any, **kwargs: Any) -> None:
    """Safely dump a Python object to a file-like object in YAML format.

    If the CSafeDumper is available, it will be used for improved performance.
    Otherwise, the SafeDumper will be used.

    Args:
        data: The Python object to dump to YAML.
        file_io: A file-like object to write the YAML content to.
        **kwargs: Additional keyword arguments to pass to yaml.dump.

    Raises:
        yaml.YAMLError: If there is an error dumping the YAML content.
    """
    yaml.dump(data, file_io, Dumper=SafeDumper, **kwargs)


def safe_dump(data: Any, **kwargs: Any) -> str:
    """Safely dump a Python object to a YAML string.

    If the CSafeDumper is available, it will be used for improved performance.
    Otherwise, the SafeDumper will be used.

    Args:
        data: The Python object to dump to YAML.
        **kwargs: Additional keyword arguments to pass to yaml.dump.

    Returns:
        A string containing the YAML representation of the Python object.

    Raises:
        yaml.YAMLError: If there is an error dumping the YAML content.
    """
    return yaml.dump(data=data, stream=None, Dumper=SafeDumper, **kwargs)  # type: ignore


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


def safe_load(text: str | bytes) -> Any:
    """Safely load YAML content from a string or bytes and return the resulting Python object.

    If the CSafeLoader is available, it will be used for improved performance.
    Otherwise, the SafeLoader will be used.

    Args:
        text: A string or bytes containing YAML content to load.

    Returns:
        The Python object resulting from parsing the YAML content.

    Raises:
        yaml.YAMLError: If there is an error parsing the YAML content.
    """
    loaded_object = yaml.load(text, Loader=SafeLoader)
    return loaded_object
