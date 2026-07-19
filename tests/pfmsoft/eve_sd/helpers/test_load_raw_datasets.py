"""Tests for eve_sd.helpers.load_raw_datasets."""

import json
from pathlib import Path

import pytest
import yaml

from pfmsoft.eve_sd.helpers.load_raw_datasets import (
    load_json_as_dataset,
    load_jsonl_as_dataset,
    load_jsonl_as_records,
    load_yaml_as_dataset,
)


class TestLoadJsonlAsDataset:
    """Tests for load_jsonl_as_dataset."""

    def test_returns_dict(self, sde_jsonl_dir: Path) -> None:
        """Result is a dict."""
        dataset = load_jsonl_as_dataset(sde_jsonl_dir / "agentTypes.jsonl")
        assert isinstance(dataset, dict)

    def test_int_keys_from_int_keyed_file(self, sde_jsonl_dir: Path) -> None:
        """Integer _key values become integer dict keys."""
        dataset = load_jsonl_as_dataset(sde_jsonl_dir / "agentTypes.jsonl")
        assert all(isinstance(k, int) for k in dataset)

    def test_str_keys_from_str_keyed_file(self, sde_jsonl_dir: Path) -> None:
        """String _key values become string dict keys."""
        dataset = load_jsonl_as_dataset(sde_jsonl_dir / "_sde.jsonl")
        assert "sde" in dataset

    def test_record_count_matches_file_lines(self, sde_jsonl_dir: Path) -> None:
        """Dataset has exactly as many entries as non-empty lines in the file."""
        dataset = load_jsonl_as_dataset(sde_jsonl_dir / "agentTypes.jsonl")
        assert len(dataset) == 3

    def test_record_contains_key_field(self, sde_jsonl_dir: Path) -> None:
        """Each record in the dataset retains the original _key field."""
        dataset = load_jsonl_as_dataset(sde_jsonl_dir / "agentTypes.jsonl")
        for key, record in dataset.items():
            assert record["_key"] == key

    def test_raises_value_error_when_line_not_a_dict(self, tmp_path: Path) -> None:
        """ValueError is raised when a JSONL line is not a JSON object."""
        bad_file = tmp_path / "bad.jsonl"
        bad_file.write_text("[1, 2, 3]\n", encoding="utf-8")
        with pytest.raises(ValueError):
            load_jsonl_as_dataset(bad_file)

    def test_raises_key_error_when_key_field_missing(self, tmp_path: Path) -> None:
        """KeyError is raised when a JSONL line has no _key field."""
        bad_file = tmp_path / "nokey.jsonl"
        bad_file.write_text('{"name": "foo"}\n', encoding="utf-8")
        with pytest.raises(KeyError):
            load_jsonl_as_dataset(bad_file)

    def test_duplicate_key_last_record_wins(self, tmp_path: Path) -> None:
        """When duplicate _key values exist the last record is kept."""
        dup_file = tmp_path / "dup.jsonl"
        dup_file.write_text(
            '{"_key": 1, "v": "first"}\n{"_key": 1, "v": "last"}\n',
            encoding="utf-8",
        )
        dataset = load_jsonl_as_dataset(dup_file)
        assert dataset[1]["v"] == "last"


class TestLoadJsonlAsRecords:
    """Tests for load_jsonl_as_records."""

    def test_yields_keyed_record_tuples(self, sde_jsonl_dir: Path) -> None:
        """Each item is a (key, record) tuple."""
        records = list(load_jsonl_as_records(sde_jsonl_dir / "agentTypes.jsonl"))
        assert len(records) == 3
        for key, record in records:
            assert isinstance(record, dict)
            assert record["_key"] == key

    def test_returns_iterable(self, sde_jsonl_dir: Path) -> None:
        """Return value is iterable (not a list or dict)."""
        result = load_jsonl_as_records(sde_jsonl_dir / "agentTypes.jsonl")
        # consume with next
        first = next(iter(result))
        assert isinstance(first, tuple)


class TestLoadJsonAsDataset:
    """Tests for load_json_as_dataset."""

    def test_loads_json_dict_file(self, tmp_path: Path) -> None:
        """JSON file with a top-level object is loaded as a dataset."""
        data = {"1": {"name": "alpha"}, "2": {"name": "beta"}}
        fp = tmp_path / "data.json"
        fp.write_text(json.dumps(data), encoding="utf-8")
        dataset = load_json_as_dataset(fp)
        assert dataset == data

    def test_raises_value_error_when_top_level_is_not_dict(
        self, tmp_path: Path
    ) -> None:
        """ValueError is raised when the JSON top level is not a dict."""
        fp = tmp_path / "list.json"
        fp.write_text("[1, 2, 3]", encoding="utf-8")
        with pytest.raises(ValueError):
            load_json_as_dataset(fp)


class TestLoadYamlAsDataset:
    """Tests for load_yaml_as_dataset."""

    def test_loads_yaml_dict_file(self, sde_yaml_dir: Path) -> None:
        """YAML file with a top-level mapping is loaded as a dataset."""
        dataset = load_yaml_as_dataset(sde_yaml_dir / "_sde.yaml")
        assert isinstance(dataset, dict)
        assert "sde" in dataset

    def test_raises_value_error_when_top_level_is_not_dict(
        self, tmp_path: Path
    ) -> None:
        """ValueError is raised when the YAML top level is not a mapping."""
        fp = tmp_path / "list.yaml"
        fp.write_text("- item1\n- item2\n", encoding="utf-8")
        with pytest.raises(ValueError):
            load_yaml_as_dataset(fp)
