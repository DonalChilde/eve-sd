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


def json_dumps(obj: Any, **kwargs: Any) -> str:
    """Dump a Python object to a JSON string."""
    return to_json(obj, **kwargs).decode("utf-8")


def json_dump_bytes(obj: Any, **kwargs: Any) -> bytes:
    """Dump a Python object to a JSON bytes."""
    return to_json(obj, **kwargs)


def json_dump_path(obj: Any, *, filepath: Path, **kwargs: Any) -> None:
    """Dump a Python object to a JSON file."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    json_string = json_dumps(obj, **kwargs)
    filepath.write_text(json_string, encoding="utf-8")
