"""Tests for SDE metadata loading and format/media detection."""

import json
from pathlib import Path

import pytest

from eve_static_data.helpers.sde_metadata import (
    SdeVariant,
    SourceMedia,
    load_sde_metadata,
)


def test_load_sde_metadata_from_json_yaml_model(tmp_path: Path) -> None:
    """JSON metadata generated from YAML should report YAML model and JSON media."""
    metadata_json = {
        "sde": {
            "buildNumber": 123456,
            "releaseDate": "2026-01-01T00:00:00Z",
        }
    }
    (tmp_path / "_sde.json").write_text(
        json.dumps(metadata_json),
        encoding="utf-8",
    )

    metadata = load_sde_metadata(tmp_path)

    assert metadata.buildNumber == 123456
    assert metadata.variant is SdeVariant.YAML
    assert metadata.source_media is SourceMedia.JSON


def test_load_sde_metadata_from_json_jsonl_model(tmp_path: Path) -> None:
    """JSON metadata generated from JSONL should report JSONL model and JSON media."""
    metadata_json = {
        "_key": "sde",
        "buildNumber": 654321,
        "releaseDate": "2026-01-02T00:00:00Z",
    }
    (tmp_path / "_sde.json").write_text(
        json.dumps(metadata_json),
        encoding="utf-8",
    )

    metadata = load_sde_metadata(tmp_path)

    assert metadata.buildNumber == 654321
    assert metadata.variant is SdeVariant.JSONL
    assert metadata.source_media is SourceMedia.JSON


def test_load_sde_metadata_rejects_multiple_metadata_files(tmp_path: Path) -> None:
    """Loader should fail when multiple _sde metadata files are present."""
    (tmp_path / "_sde.yaml").write_text(
        "sde:\n  buildNumber: 1\n  releaseDate: '2026-01-01T00:00:00Z'\n",
        encoding="utf-8",
    )
    (tmp_path / "_sde.json").write_text(
        json.dumps({"sde": {"buildNumber": 1, "releaseDate": "2026-01-01T00:00:00Z"}}),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Multiple _sde metadata files"):
        load_sde_metadata(tmp_path)
