"""Tests for eve_sd.helpers.write_dicts_to_csv."""

import csv
from pathlib import Path

import pytest

from eve_sd.helpers.write_dicts_to_csv import write_dicts_to_csv


class TestWriteDictsToCsv:
    """Tests for write_dicts_to_csv."""

    def test_writes_header_and_data_rows(self, tmp_path: Path) -> None:
        """CSV file contains a header row derived from the first dict's keys."""
        out = tmp_path / "out.csv"
        write_dicts_to_csv([{"a": 1, "b": 2}, {"a": 3, "b": 4}], out)
        with out.open(encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        assert reader.fieldnames == ["a", "b"]
        assert rows[0] == {"a": "1", "b": "2"}
        assert rows[1] == {"a": "3", "b": "4"}

    def test_returns_correct_row_count(self, tmp_path: Path) -> None:
        """Return value equals the number of data rows written."""
        out = tmp_path / "count.csv"
        count = write_dicts_to_csv([{"x": i} for i in range(5)], out)
        assert count == 5

    def test_empty_iterable_creates_empty_file(self, tmp_path: Path) -> None:
        """Empty input creates an empty file and returns 0."""
        out = tmp_path / "empty.csv"
        count = write_dicts_to_csv(iter([]), out)
        assert count == 0
        assert out.exists()
        assert out.stat().st_size == 0

    def test_raises_file_exists_error_when_file_exists_no_overwrite(
        self, tmp_path: Path
    ) -> None:
        """FileExistsError is raised when the target file exists and overwrite=False."""
        out = tmp_path / "dup.csv"
        write_dicts_to_csv([{"a": 1}], out)
        with pytest.raises(FileExistsError):
            write_dicts_to_csv([{"a": 2}], out, overwrite=False)

    def test_overwrites_existing_file_when_overwrite_true(self, tmp_path: Path) -> None:
        """Existing file is replaced when overwrite=True."""
        out = tmp_path / "ow.csv"
        write_dicts_to_csv([{"a": 1}], out)
        write_dicts_to_csv([{"a": 99}], out, overwrite=True)
        with out.open(encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        assert rows == [{"a": "99"}]

    def test_raises_file_exists_error_when_path_is_existing_dir(
        self, tmp_path: Path
    ) -> None:
        """FileExistsError is raised when the path points to an existing directory."""
        with pytest.raises(FileExistsError):
            write_dicts_to_csv([{"a": 1}], tmp_path)

    def test_raises_is_a_directory_error_with_overwrite(self, tmp_path: Path) -> None:
        """IsADirectoryError is raised when overwrite=True and path is a directory."""
        with pytest.raises(IsADirectoryError):
            write_dicts_to_csv([{"a": 1}], tmp_path, overwrite=True)

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Missing parent directories are created before writing."""
        out = tmp_path / "nested" / "deep" / "data.csv"
        write_dicts_to_csv([{"a": 1}], out)
        assert out.exists()

    def test_single_row(self, tmp_path: Path) -> None:
        """A single-row input is written correctly."""
        out = tmp_path / "one.csv"
        count = write_dicts_to_csv([{"name": "Eve", "id": "42"}], out)
        assert count == 1
        with out.open(encoding="utf-8") as f:
            content = f.read()
        assert "name" in content
        assert "Eve" in content
