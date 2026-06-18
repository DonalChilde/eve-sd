"""Helper functions for loading and dumping JSON data using the pydantic json library."""

from io import TextIOWrapper
from pathlib import Path
from typing import Any, Iterator

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


def jsonl_loads(jsonl_string: str | bytes) -> Iterator[Any]:
    """Load a JSONL string into a list of Python objects."""
    for line in jsonl_string.splitlines():
        if line.strip():
            yield from_json(line)


def jsonl_load_path(filepath: Path) -> Iterator[Any]:
    """Load a JSONL file into a list of Python objects."""
    with filepath.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield from_json(line)


def jsonl_dump_path(
    objs: Iterator[Any],
    *,
    filepath: Path,
    overwrite: bool = False,
    append: bool = False,
    indent: int | None = None,
    **kwargs: Any,
) -> int:
    """Dump a list of Python objects to a JSONL file.

    Uses Pydantic's `to_json` function to serialize the objects.
    Writes one JSON object per line in the file, does not load the entire file into memory at once.

    overwrite and append are mutually exclusive. If both are True, raises a ValueError.

    Args:
        objs: An iterator of Python objects to dump.
        filepath: The path to the JSONL file.
        overwrite: Whether to overwrite the file if it exists.
        append: Whether to append to the file if it exists.
        indent: The indentation level for the JSONL file.
        **kwargs: Additional keyword arguments passed to `json_dumps`.

    Returns:
        The number of characters written to the file.

    Raises:
        FileExistsError: If the file already exists and `overwrite` is False.
    """
    filepath.parent.mkdir(parents=True, exist_ok=True)
    if overwrite and append:
        raise ValueError("overwrite and append are mutually exclusive.")

    def write_objs(f: TextIOWrapper):
        counter = 0
        for obj in objs:
            counter += f.write(json_dumps(obj, indent=indent, **kwargs))
            counter += f.write("\n")
        return counter

    if append:
        with filepath.open("a", encoding="utf-8") as f:
            return write_objs(f)

    if overwrite:
        with filepath.open("w", encoding="utf-8") as f:
            return write_objs(f)
    else:
        with filepath.open("x", encoding="utf-8") as f:
            return write_objs(f)


def jsonl_dumps(objs: Iterator[Any], indent: int | None = None, **kwargs: Any) -> str:
    """Dump a list of Python objects to a JSONL string."""
    return "\n".join(json_dumps(obj, indent=indent, **kwargs) for obj in objs)
