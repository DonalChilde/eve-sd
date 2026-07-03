"""Fixtures shared across eve_sd.db tests."""

import sqlite3
from pathlib import Path

import pytest

from eve_sd.db.helpers import create_read_write_connection
from eve_sd.helpers.sde_metadata import SdeMetadata, SdeVariant, SourceMedia


@pytest.fixture
def rw_connection(tmp_path: Path) -> sqlite3.Connection:
    """Return a fresh read-write SQLite connection with schema bootstrapped."""
    db_path = str(tmp_path / "test.db")
    conn = create_read_write_connection(db_path)
    yield conn
    conn.close()


@pytest.fixture
def sample_metadata() -> SdeMetadata:
    """Return a minimal SdeMetadata for testing."""
    return SdeMetadata(
        buildNumber=9999,
        releaseDate="2025-01-01T00:00:00Z",
        variant=SdeVariant.JSONL,
        source_media=SourceMedia.JSONL,
    )


@pytest.fixture
def sample_int_records() -> list[tuple[int, dict]]:
    """A short list of integer-keyed (key, record) tuples."""
    return [
        (1, {"_key": 1, "name": "Alpha"}),
        (2, {"_key": 2, "name": "Beta"}),
        (3, {"_key": 3, "name": "Gamma"}),
    ]


@pytest.fixture
def sample_str_records() -> list[tuple[str, dict]]:
    """A short list of string-keyed (key, record) tuples."""
    return [
        ("sde", {"_key": "sde", "buildNumber": 9999}),
        ("meta", {"_key": "meta", "buildNumber": 8888}),
    ]
