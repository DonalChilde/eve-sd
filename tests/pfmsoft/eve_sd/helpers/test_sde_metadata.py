"""Tests for eve_sd.helpers.sde_metadata."""

import zipfile
from pathlib import Path

import pytest

from pfmsoft.eve_sd.helpers.sde_metadata import (
    SdeMetadata,
    SdeVariant,
    SourceMedia,
    load_sde_metadata,
    load_sde_metadata_from_zipfile,
)


class TestLoadSdeMetadataFromJsonl:
    """Tests for load_sde_metadata with a JSONL metadata file."""

    def test_returns_sde_metadata_instance(self, sde_jsonl_dir: Path) -> None:
        """Result is an SdeMetadata dataclass instance."""
        metadata = load_sde_metadata(sde_jsonl_dir)
        assert isinstance(metadata, SdeMetadata)

    def test_parses_build_number(self, sde_jsonl_dir: Path) -> None:
        """buildNumber is correctly parsed as an int."""
        metadata = load_sde_metadata(sde_jsonl_dir)
        assert metadata.buildNumber == 3294658

    def test_parses_release_date(self, sde_jsonl_dir: Path) -> None:
        """releaseDate is correctly parsed as a string."""
        metadata = load_sde_metadata(sde_jsonl_dir)
        assert metadata.releaseDate == "2026-04-09T11:29:37Z"

    def test_variant_is_jsonl(self, sde_jsonl_dir: Path) -> None:
        """variant is SdeVariant.JSONL when loaded from a .jsonl file."""
        metadata = load_sde_metadata(sde_jsonl_dir)
        assert metadata.variant == SdeVariant.JSONL

    def test_source_media_is_jsonl(self, sde_jsonl_dir: Path) -> None:
        """source_media is SourceMedia.JSONL when loaded from a .jsonl file."""
        metadata = load_sde_metadata(sde_jsonl_dir)
        assert metadata.source_media == SourceMedia.JSONL


class TestLoadSdeMetadataFromYaml:
    """Tests for load_sde_metadata with a YAML metadata file."""

    def test_returns_sde_metadata_instance(self, sde_yaml_dir: Path) -> None:
        """Result is an SdeMetadata dataclass instance."""
        metadata = load_sde_metadata(sde_yaml_dir)
        assert isinstance(metadata, SdeMetadata)

    def test_parses_build_number(self, sde_yaml_dir: Path) -> None:
        """buildNumber is correctly parsed as an int from YAML."""
        metadata = load_sde_metadata(sde_yaml_dir)
        assert metadata.buildNumber == 3321490

    def test_parses_release_date(self, sde_yaml_dir: Path) -> None:
        """releaseDate is correctly parsed as a string from YAML."""
        metadata = load_sde_metadata(sde_yaml_dir)
        assert metadata.releaseDate == "2026-04-28T11:43:10Z"

    def test_variant_is_yaml(self, sde_yaml_dir: Path) -> None:
        """variant is SdeVariant.YAML when loaded from a .yaml file."""
        metadata = load_sde_metadata(sde_yaml_dir)
        assert metadata.variant == SdeVariant.YAML

    def test_source_media_is_yaml(self, sde_yaml_dir: Path) -> None:
        """source_media is SourceMedia.YAML when loaded from a .yaml file."""
        metadata = load_sde_metadata(sde_yaml_dir)
        assert metadata.source_media == SourceMedia.YAML


class TestLoadSdeMetadataErrors:
    """Tests for load_sde_metadata error cases."""

    def test_raises_file_not_found_when_no_metadata_file(self, tmp_path: Path) -> None:
        """FileNotFoundError is raised when neither _sde.jsonl nor _sde.yaml exists."""
        with pytest.raises(FileNotFoundError):
            load_sde_metadata(tmp_path)

    def test_raises_value_error_when_both_metadata_files_present(
        self, tmp_path: Path
    ) -> None:
        """ValueError is raised when both _sde.jsonl and _sde.yaml exist."""
        (tmp_path / "_sde.jsonl").write_text(
            '{"_key": "sde", "buildNumber": 1, "releaseDate": "2025-01-01T00:00:00Z"}\n',
            encoding="utf-8",
        )
        (tmp_path / "_sde.yaml").write_text(
            "sde:\n  buildNumber: 1\n  releaseDate: '2025-01-01T00:00:00Z'\n",
            encoding="utf-8",
        )
        with pytest.raises(ValueError):
            load_sde_metadata(tmp_path)


class TestLoadSdeMetadataFromZipfile:
    """Tests for load_sde_metadata_from_zipfile."""

    def _make_zip(self, tmp_path: Path, filename: str, content: str) -> Path:
        """Helper: create a zip file with a single metadata member."""
        zip_path = tmp_path / "sde.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr(filename, content)
        return zip_path

    def test_reads_metadata_from_jsonl_in_zip(self, tmp_path: Path) -> None:
        """SdeMetadata is extracted from a _sde.jsonl inside a zip archive."""
        content = '{"_key": "sde", "buildNumber": 9999, "releaseDate": "2025-06-01T12:00:00Z"}\n'
        zip_path = self._make_zip(tmp_path, "_sde.jsonl", content)
        metadata = load_sde_metadata_from_zipfile(zip_path)
        assert metadata.buildNumber == 9999
        assert metadata.variant == SdeVariant.JSONL

    def test_reads_metadata_from_yaml_in_zip(self, tmp_path: Path) -> None:
        """SdeMetadata is extracted from a _sde.yaml inside a zip archive."""
        content = "sde:\n  buildNumber: 8888\n  releaseDate: '2025-05-01T00:00:00Z'\n"
        zip_path = self._make_zip(tmp_path, "_sde.yaml", content)
        metadata = load_sde_metadata_from_zipfile(zip_path)
        assert metadata.buildNumber == 8888
        assert metadata.variant == SdeVariant.YAML
