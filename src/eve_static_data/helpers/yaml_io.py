"""YAML load/dump helpers with safe loader/dumper defaults.

The module prefers ``yaml.CSafeLoader``/``yaml.CSafeDumper`` when available and
falls back to pure-Python safe implementations otherwise.
"""

import logging
from pathlib import Path
from typing import IO, Any, TextIO

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
    """Serialize a Python object to a YAML file.

    Args:
        data: The Python object to dump to YAML.
        file_path: Destination YAML file path.
        **kwargs: Additional keyword arguments forwarded to ``yaml.dump``.

    Raises:
        yaml.YAMLError: If YAML serialization fails.
    """
    with file_path.open("w") as f:
        yaml.dump(data, f, Dumper=SafeDumper, **kwargs)


def safe_dump_IO(data: Any, file_io: TextIO, **kwargs: Any) -> None:
    """Serialize a Python object to an existing file-like object.

    Args:
        data: The Python object to dump to YAML.
        file_io: Writable file-like object.
        **kwargs: Additional keyword arguments forwarded to ``yaml.dump``.

    Raises:
        yaml.YAMLError: If YAML serialization fails.

    Notes:
        Stream lifecycle is managed by the caller; this function does not close
        the file object.
    """
    yaml.dump(data, file_io, Dumper=SafeDumper, **kwargs)


def safe_dump(data: Any, **kwargs: Any) -> str:
    """Serialize a Python object to a YAML string.

    Args:
        data: The Python object to dump to YAML.
        **kwargs: Additional keyword arguments forwarded to ``yaml.dump``.

    Returns:
        YAML text representation of ``data``.

    Raises:
        yaml.YAMLError: If YAML serialization fails.
    """
    return yaml.dump(data=data, stream=None, Dumper=SafeDumper, **kwargs)  # type: ignore


def safe_load_path(file_path: Path) -> Any:
    """Parse a YAML file into Python objects.

    Args:
        file_path: Source YAML file path.

    Returns:
        Python object parsed from YAML content.

    Raises:
        yaml.YAMLError: If YAML parsing fails.
        FileNotFoundError: If ``file_path`` does not exist.
    """
    with file_path.open() as f:
        loaded_object = yaml.load(f, Loader=SafeLoader)
    return loaded_object


def safe_load_IO(file_io: IO[str] | IO[bytes]) -> Any:
    """Parse YAML content from an existing file-like object.

    Args:
        file_io: Readable file-like object containing YAML text.

    Returns:
        Python object parsed from YAML content.

    Raises:
        yaml.YAMLError: If YAML parsing fails.

    Notes:
        Stream lifecycle is managed by the caller; this function does not close
        the file object.
    """
    loaded_object = yaml.load(file_io, Loader=SafeLoader)
    return loaded_object


def safe_load(text: str | bytes) -> Any:
    """Parse YAML content from a string or bytes object.

    Args:
        text: YAML text or bytes payload.

    Returns:
        Python object parsed from YAML content.

    Raises:
        yaml.YAMLError: If YAML parsing fails.
    """
    loaded_object = yaml.load(text, Loader=SafeLoader)
    return loaded_object
