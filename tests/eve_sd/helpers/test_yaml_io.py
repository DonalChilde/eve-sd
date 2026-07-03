"""Tests for eve_sd.helpers.yaml_io."""

import io
from pathlib import Path

from eve_sd.helpers import yaml_io

SAMPLE: dict[str, object] = {"name": "Eve", "version": 1, "active": True}


class TestSafeDumpAndLoad:
    """Tests for safe_dump / safe_load round-trips."""

    def test_safe_dump_returns_string(self) -> None:
        """safe_dump returns a YAML-formatted string."""
        result = yaml_io.safe_dump(SAMPLE)
        assert isinstance(result, str)
        assert "Eve" in result

    def test_safe_load_string_round_trip(self) -> None:
        """safe_dump → safe_load round-trip preserves the object."""
        serialized = yaml_io.safe_dump(SAMPLE)
        restored = yaml_io.safe_load(serialized)
        assert restored == SAMPLE

    def test_safe_load_bytes_round_trip(self) -> None:
        """safe_load accepts bytes as well as a string."""
        serialized = yaml_io.safe_dump(SAMPLE).encode("utf-8")
        restored = yaml_io.safe_load(serialized)
        assert restored == SAMPLE

    def test_safe_dump_io_writes_to_stream(self) -> None:
        """safe_dump_IO writes YAML to a file-like object."""
        buf = io.StringIO()
        yaml_io.safe_dump_IO(SAMPLE, buf)
        content = buf.getvalue()
        assert "Eve" in content

    def test_safe_load_io_reads_from_stream(self) -> None:
        """safe_load_IO reads YAML from a file-like object."""
        serialized = yaml_io.safe_dump(SAMPLE)
        buf = io.StringIO(serialized)
        restored = yaml_io.safe_load_IO(buf)
        assert restored == SAMPLE


class TestFilePath:
    """Tests for safe_dump_path / safe_load_path."""

    def test_dump_path_creates_file(self, tmp_path: Path) -> None:
        """safe_dump_path writes a YAML file at the given path."""
        fp = tmp_path / "data.yaml"
        yaml_io.safe_dump_path(SAMPLE, fp)
        assert fp.exists()
        assert fp.stat().st_size > 0

    def test_load_path_reads_file(self, tmp_path: Path) -> None:
        """safe_load_path returns the object written by safe_dump_path."""
        fp = tmp_path / "data.yaml"
        yaml_io.safe_dump_path(SAMPLE, fp)
        restored = yaml_io.safe_load_path(fp)
        assert restored == SAMPLE

    def test_round_trip_with_nested_data(self, tmp_path: Path) -> None:
        """Nested dicts and lists survive a dump/load round-trip."""
        nested: dict[str, object] = {
            "outer": {"inner": [1, 2, 3]},
            "tags": ["a", "b"],
        }
        fp = tmp_path / "nested.yaml"
        yaml_io.safe_dump_path(nested, fp)
        assert yaml_io.safe_load_path(fp) == nested

    def test_load_real_sde_yaml_file(self, sde_yaml_dir: Path) -> None:
        """A real SDE YAML file is loaded without error."""
        fp = sde_yaml_dir / "_sde.yaml"
        data = yaml_io.safe_load_path(fp)
        assert isinstance(data, dict)
        assert "sde" in data
        assert "buildNumber" in data["sde"]
