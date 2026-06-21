"""Tests for the SDE YAML dataset loader."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest
import yaml
from pydantic import RootModel

import tests.resources.sde_data.yaml as _yaml_pkg
from eve_static_data.access.yaml_datasets import SdeYamlDatasetLoader
from eve_static_data.models.dataset_filenames import SdeDatasets
from eve_static_data.models.yaml_format import yaml_datasets_dc

# Directory of the committed YAML fixture files — used directly for happy-path tests.
YAML_FIXTURE_DIR = Path(_yaml_pkg.__file__).parent


@dataclass(frozen=True)
class LoaderCase:
    """Configuration for a dataset loader method test."""

    case_id: str
    method_name: str
    fixture_file_name: str
    root_model: type[RootModel[Any]]


# Add new loader method entries here as yaml_datasets.py grows.
LOADER_CASES: list[LoaderCase] = [
    LoaderCase(
        case_id="agent_types",
        method_name="agent_types",
        fixture_file_name="agentTypes.yaml",
        root_model=yaml_datasets_dc.AgentTypesRoot,
    ),
    LoaderCase(
        case_id="agents_in_space",
        method_name="agents_in_space",
        fixture_file_name="agentsInSpace.yaml",
        root_model=yaml_datasets_dc.AgentsInSpaceRoot,
    ),
]


def _read_yaml_fixture(file_name: str) -> dict[Any, Any]:
    """Load a YAML fixture from the committed fixture directory."""
    with (YAML_FIXTURE_DIR / file_name).open(encoding="utf-8") as fh:
        loaded: Any = yaml.safe_load(fh)
    assert isinstance(loaded, dict)
    return loaded


# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------


def test_loader_reads_sde_metadata_from_yaml() -> None:
    """Loader should read file type and metadata from the committed YAML _sde file."""
    loader = SdeYamlDatasetLoader(YAML_FIXTURE_DIR)

    assert loader.file_type == ".yaml"
    assert loader.buildNumber > -1
    assert loader.releaseDate


# JSON-mode metadata test will be added once a JSON fixture directory is available.


@pytest.mark.parametrize(
    ("sde_files", "error_message"),
    [
        ((), "No _sde file found in the provided path"),
        (("_sde.yaml", "_sde.json"), "Multiple _sde files found in the provided path"),
    ],
)
def test_loader_requires_exactly_one_sde_file(
    tmp_path: Path,
    sde_files: tuple[str, ...],
    error_message: str,
) -> None:
    """Loader initialization should fail unless exactly one _sde file is present."""
    sde_text = (YAML_FIXTURE_DIR / "_sde.yaml").read_text(encoding="utf-8")
    sde_dict = _read_yaml_fixture("_sde.yaml")
    for file_name in sde_files:
        content = json.dumps(sde_dict) if file_name.endswith(".json") else sde_text
        (tmp_path / file_name).write_text(content, encoding="utf-8")

    with pytest.raises(ValueError, match=error_message):
        SdeYamlDatasetLoader(tmp_path)


# ---------------------------------------------------------------------------
# Path narrowing
# ---------------------------------------------------------------------------


def test_narrow_file_path_returns_yaml_path_for_yaml_sde() -> None:
    """Path narrowing should resolve the YAML dataset file in a YAML SDE directory."""
    loader = SdeYamlDatasetLoader(YAML_FIXTURE_DIR)
    expected = YAML_FIXTURE_DIR / SdeDatasets.AGENT_TYPES.as_yaml()

    assert loader._narrow_file_path(SdeDatasets.AGENT_TYPES) == expected


def test_narrow_file_path_raises_when_dataset_missing(tmp_path: Path) -> None:
    """Path narrowing should raise FileNotFoundError when the dataset file is absent."""
    (tmp_path / "_sde.yaml").write_text(
        (YAML_FIXTURE_DIR / "_sde.yaml").read_text(encoding="utf-8"), encoding="utf-8"
    )
    loader = SdeYamlDatasetLoader(tmp_path)

    with pytest.raises(FileNotFoundError, match="agentTypes.yaml"):
        loader._narrow_file_path(SdeDatasets.AGENT_TYPES)


# ---------------------------------------------------------------------------
# Dataset loader methods
# ---------------------------------------------------------------------------

# FIXME Change so that test cases are generated from SdeDatasetFiles, and various lookups.


@pytest.mark.parametrize("case", LOADER_CASES, ids=lambda case: case.case_id)
def test_dataset_loader_methods_return_validated_root_models(case: LoaderCase) -> None:
    """Each loader method should return a validated root model matching the fixture."""
    loader = SdeYamlDatasetLoader(YAML_FIXTURE_DIR)
    loaded = getattr(loader, case.method_name)()

    expected = case.root_model.model_validate(
        _read_yaml_fixture(case.fixture_file_name)
    )
    assert isinstance(loaded, case.root_model)
    assert loaded.model_dump(mode="python") == expected.model_dump(mode="python")
