"""Fixtures for eve_sd helpers tests."""

from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def sde_data_dir() -> Path:
    """Return the path to the SDE test data directory."""
    return Path(__file__).parent.parent.parent.parent / "resources" / "sde_data"


@pytest.fixture(scope="session")
def sde_jsonl_dir(sde_data_dir: Path) -> Path:
    """Return the path to the JSONL test data directory."""
    return sde_data_dir / "jsonl"


@pytest.fixture(scope="session")
def sde_yaml_dir(sde_data_dir: Path) -> Path:
    """Return the path to the YAML test data directory."""
    return sde_data_dir / "yaml"
