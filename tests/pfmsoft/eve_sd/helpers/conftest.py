"""Fixtures for eve_sd helpers tests."""

from importlib.resources import files
from importlib.resources.abc import Traversable

import pytest


@pytest.fixture(scope="session")
def sde_data_dir() -> Traversable:
    """Return the path to the SDE test data directory."""
    return files("tests.resources").joinpath("sde_data")


@pytest.fixture(scope="session")
def sde_jsonl_dir(sde_data_dir: Traversable) -> Traversable:
    """Return the path to the JSONL test data directory."""
    return sde_data_dir.joinpath("jsonl")


@pytest.fixture(scope="session")
def sde_yaml_dir(sde_data_dir: Traversable) -> Traversable:
    """Return the path to the YAML test data directory."""
    return sde_data_dir.joinpath("yaml")
