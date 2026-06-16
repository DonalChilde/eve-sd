"""Helper functions for loading and dumping JSON data using the pydantic json library."""

from pathlib import Path
from typing import Any

from pydantic_core import from_json, to_json


def json_load_path(filepath: Path) -> Any:
    """Load a JSON string into a Python object."""
    return from_json(filepath.read_text(encoding="utf-8"))


def json_loads(json_string: str | bytes) -> Any:
    """Load a JSON string into a Python object."""
    return from_json(json_string)


def json_dumps(obj: Any, indent: int | None = None, **kwargs: Any) -> str:
    """Dump a Python object to a JSON string."""
    return to_json(obj, indent=indent, **kwargs).decode("utf-8")


def json_dump_bytes(obj: Any, indent: int | None = None, **kwargs: Any) -> bytes:
    """Dump a Python object to a JSON bytes."""
    return to_json(obj, indent=indent, **kwargs)


def json_dump_path(
    obj: Any,
    *,
    filepath: Path,
    overwrite: bool = False,
    indent: int | None = None,
    **kwargs: Any,
) -> int:
    """Dump a Python object to a JSON file.

    Uses Pydantic's `to_json` function to serialize the object.

    Args:
        obj: The Python object to dump.
        filepath: The path to the JSON file.
        overwrite: Whether to overwrite the file if it exists.
        indent: The indentation level for the JSON file.
        **kwargs: Additional keyword arguments passed to `json_dumps`.

    Returns:
        The number of characters written to the file.

    Raises:
        FileExistsError: If the file already exists and `overwrite` is False.
    """
    filepath.parent.mkdir(parents=True, exist_ok=True)
    if overwrite:
        with filepath.open("w", encoding="utf-8") as f:
            counter = 0
            counter += f.write(json_dumps(obj, indent=indent, **kwargs))
            counter += f.write("\n")
            return counter
    else:
        with filepath.open("x", encoding="utf-8") as f:
            counter = 0
            counter += f.write(json_dumps(obj, indent=indent, **kwargs))
            counter += f.write("\n")
            return counter
