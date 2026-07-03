"""YAML load/dump helpers with safe loader/dumper defaults.

The module prefers ``yaml.CSafeLoader``/``yaml.CSafeDumper`` when available and
falls back to pure-Python safe implementations otherwise.
"""

import logging
from pathlib import Path
from typing import IO, Any, BinaryIO, TextIO

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


def safe_dump_str_path(
    data: Any,
    file_path: Path,
    *,
    overwrite: bool = False,
    encoding: str = "utf-8",
    allow_unicode: bool = True,
    **kwargs: Any,
) -> None:
    """Serialize a Python object to a YAML file.

    Args:
        data: The Python object to dump to YAML.
        file_path: Destination YAML file path.
        overwrite: Whether to overwrite the file if it already exists.
        encoding: File encoding to use.
        allow_unicode: Whether to allow non-ASCII characters in the output.
        **kwargs: Additional keyword arguments forwarded to ``yaml.dump``.

    Raises:
        yaml.YAMLError: If YAML serialization fails.
        FileExistsError: If the target file exists and ``overwrite`` is false.
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)

    if overwrite:
        mode = "w"
    else:
        mode = "x"

    with file_path.open(mode, encoding=encoding) as f:
        yaml.dump(
            data, stream=f, Dumper=SafeDumper, allow_unicode=allow_unicode, **kwargs
        )


def safe_dump_bytes_path(
    data: Any,
    file_path: Path,
    *,
    overwrite: bool = False,
    encoding: str = "utf-8",
    allow_unicode: bool = True,
    **kwargs: Any,
) -> None:
    """Serialize a Python object to a YAML file in binary mode.

    Args:
        data: The Python object to dump to YAML.
        file_path: Destination YAML file path.
        overwrite: Whether to overwrite the file if it already exists.
        encoding: File encoding to use.
        allow_unicode: Whether to allow non-ASCII characters in the output.
        **kwargs: Additional keyword arguments forwarded to ``yaml.dump``.

    Raises:
        yaml.YAMLError: If YAML serialization fails.
        FileExistsError: If the target file exists and ``overwrite`` is false.
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)
    if overwrite:
        mode = "wb"
    else:
        mode = "xb"
    with file_path.open(mode) as f:
        yaml.dump(
            data,
            stream=f,
            Dumper=SafeDumper,
            allow_unicode=allow_unicode,
            encoding=encoding,
            **kwargs,
        )


def safe_dump_text_io(
    data: Any, file_io: TextIO, *, allow_unicode: bool = True, **kwargs: Any
) -> None:
    """Serialize a Python object to an existing file-like object.

    Args:
        data: The Python object to dump to YAML.
        file_io: Writable file-like object.
        allow_unicode: Whether to allow non-ASCII characters in the output.
        **kwargs: Additional keyword arguments forwarded to ``yaml.dump``.

    Raises:
        yaml.YAMLError: If YAML serialization fails.

    Notes:
        Stream lifecycle is managed by the caller; this function does not close
        the file object.
    """
    yaml.dump(
        data,
        stream=file_io,
        encoding=None,
        Dumper=SafeDumper,
        allow_unicode=allow_unicode,
        **kwargs,
    )


def safe_dump_binary_io(
    data: Any,
    file_io: BinaryIO,
    *,
    allow_unicode: bool = True,
    encoding: str = "utf-8",
    **kwargs: Any,
) -> None:
    """Serialize a Python object to an existing binary file-like object.

    Args:
        data: The Python object to dump to YAML.
        file_io: Writable binary file-like object.
        allow_unicode: Whether to allow non-ASCII characters in the output.
        encoding: The encoding to use for the byte string.
        **kwargs: Additional keyword arguments forwarded to ``yaml.dump``.

    Raises:
        yaml.YAMLError: If YAML serialization fails.

    Notes:
        Stream lifecycle is managed by the caller; this function does not close
        the file object.
    """
    yaml.dump(
        data,
        stream=file_io,
        Dumper=SafeDumper,
        allow_unicode=allow_unicode,
        encoding=encoding,
        **kwargs,
    )


def safe_dump_str(data: Any, *, allow_unicode: bool = True, **kwargs: Any) -> str:
    """Serialize a Python object to a YAML string.

    Args:
        data: The Python object to dump to YAML.
        allow_unicode: Whether to allow non-ASCII characters in the output.
        **kwargs: Additional keyword arguments forwarded to ``yaml.dump``.

    Returns:
        YAML text representation of ``data``.

    Raises:
        yaml.YAMLError: If YAML serialization fails.
    """
    result = yaml.dump(
        data=data,
        stream=None,
        encoding=None,
        Dumper=SafeDumper,
        allow_unicode=allow_unicode,
        **kwargs,
    )
    return result


def safe_dump_bytes(
    data: Any, *, allow_unicode: bool = True, encoding: str = "utf-8", **kwargs: Any
) -> bytes:
    """Serialize a Python object to a YAML byte string.

    Args:
        data: The Python object to dump to YAML.
        allow_unicode: Whether to allow non-ASCII characters in the output.
        encoding: The encoding to use for the byte string.
        **kwargs: Additional keyword arguments forwarded to ``yaml.dump``.

    Returns:
        YAML byte string representation of ``data``.

    Raises:
        yaml.YAMLError: If YAML serialization fails.
    """
    yaml_bytes = yaml.dump(
        data=data,
        stream=None,
        Dumper=SafeDumper,
        allow_unicode=allow_unicode,
        encoding=encoding,
        **kwargs,
    )
    if not isinstance(yaml_bytes, bytes):
        raise TypeError(
            f"Expected bytes from safe_dump, got {type(yaml_bytes).__name__}"
        )
    return yaml_bytes


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
