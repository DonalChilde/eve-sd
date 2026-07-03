"""Tests for eve_sd.helpers.json_io."""

from pathlib import Path

import pytest

from eve_sd.helpers import json_io

SAMPLE_OBJ: dict[str, object] = {"key": "value", "num": 42, "flag": True}
SAMPLE_JSONL_STR = '{"a":1}\n{"b":2}\n{"c":3}\n'
SAMPLE_JSONL_WITH_BLANKS = '{"a":1}\n\n{"b":2}\n\n'


class TestJsonRoundTrip:
    """Tests for JSON serialization helpers."""

    def test_json_dumps_produces_string(self) -> None:
        """json_dumps returns a str."""
        result = json_io.json_dumps(SAMPLE_OBJ)
        assert isinstance(result, str)

    def test_json_dump_bytes_produces_bytes(self) -> None:
        """json_dump_bytes returns bytes."""
        result = json_io.json_dump_bytes(SAMPLE_OBJ)
        assert isinstance(result, bytes)

    def test_json_loads_string_round_trip(self) -> None:
        """Object survives a dumps → loads round-trip via string."""
        serialized = json_io.json_dumps(SAMPLE_OBJ)
        restored = json_io.json_loads(serialized)
        assert restored == SAMPLE_OBJ

    def test_json_loads_bytes_round_trip(self) -> None:
        """Object survives a dump_bytes → loads round-trip via bytes."""
        serialized = json_io.json_dump_bytes(SAMPLE_OBJ)
        restored = json_io.json_loads(serialized)
        assert restored == SAMPLE_OBJ

    def test_json_dumps_with_indent(self) -> None:
        """indent parameter produces multi-line output."""
        result = json_io.json_dumps({"a": 1}, indent=2)
        assert "\n" in result


class TestJsonFilePath:
    """Tests for json_dump_path / json_load_path."""

    def test_dump_and_load_path_round_trip(self, tmp_path: Path) -> None:
        """Object survives dump → load round-trip via file."""
        fp = tmp_path / "data.json"
        json_io.json_dump_path(SAMPLE_OBJ, filepath=fp)
        restored = json_io.json_load_path(fp)
        assert restored == SAMPLE_OBJ

    def test_dump_path_creates_parent_dirs(self, tmp_path: Path) -> None:
        """json_dump_path creates missing parent directories."""
        fp = tmp_path / "sub" / "dir" / "data.json"
        json_io.json_dump_path({"x": 1}, filepath=fp)
        assert fp.exists()

    def test_dump_path_raises_file_exists_error_no_overwrite(
        self, tmp_path: Path
    ) -> None:
        """FileExistsError is raised when target exists and overwrite=False."""
        fp = tmp_path / "dup.json"
        json_io.json_dump_path({}, filepath=fp)
        with pytest.raises(FileExistsError):
            json_io.json_dump_path({}, filepath=fp, overwrite=False)

    def test_dump_path_overwrites_when_overwrite_true(self, tmp_path: Path) -> None:
        """Existing file is replaced when overwrite=True."""
        fp = tmp_path / "ow.json"
        json_io.json_dump_path({"v": 1}, filepath=fp)
        json_io.json_dump_path({"v": 99}, filepath=fp, overwrite=True)
        assert json_io.json_load_path(fp) == {"v": 99}

    def test_dump_path_returns_bytes_written(self, tmp_path: Path) -> None:
        """Return value is a positive integer (bytes written)."""
        fp = tmp_path / "count.json"
        written = json_io.json_dump_path(SAMPLE_OBJ, filepath=fp)
        assert written > 0


class TestJsonlFromString:
    """Tests for JSONL parsing from strings."""

    def test_jsonl_loads_yields_objects(self) -> None:
        """jsonl_loads yields one object per non-empty line."""
        results = list(json_io.jsonl_loads(SAMPLE_JSONL_STR))
        assert results == [{"a": 1}, {"b": 2}, {"c": 3}]

    def test_jsonl_loads_skips_blank_lines(self) -> None:
        """jsonl_loads skips blank lines without error."""
        results = list(json_io.jsonl_loads(SAMPLE_JSONL_WITH_BLANKS))
        assert results == [{"a": 1}, {"b": 2}]

    def test_jsonl_loads_indexed_yields_line_numbers(self) -> None:
        """jsonl_loads_indexed yields (line_number, obj) tuples starting at 1."""
        results = list(json_io.jsonl_loads_indexed(SAMPLE_JSONL_STR))
        assert results[0] == (1, {"a": 1})
        assert results[1] == (2, {"b": 2})
        assert results[2] == (3, {"c": 3})

    def test_jsonl_loads_indexed_blank_lines_affect_numbering(self) -> None:
        """Blank lines increment the line counter but are not yielded."""
        results = list(json_io.jsonl_loads_indexed(SAMPLE_JSONL_WITH_BLANKS))
        # Line 1 = {"a":1}, line 2 = blank, line 3 = {"b":2}
        assert results[0][0] == 1
        assert results[1][0] == 3

    def test_jsonl_loads_empty_string(self) -> None:
        """Empty input yields no objects."""
        assert list(json_io.jsonl_loads("")) == []


class TestJsonlFromBytes:
    """Tests for JSONL parsing from bytes."""

    def test_jsonl_load_bytes_yields_objects(self) -> None:
        """jsonl_load_bytes yields one object per non-empty line."""
        data = SAMPLE_JSONL_STR.encode("utf-8")
        results = list(json_io.jsonl_load_bytes(data))
        assert results == [{"a": 1}, {"b": 2}, {"c": 3}]

    def test_jsonl_load_bytes_indexed_yields_tuples(self) -> None:
        """jsonl_load_bytes_indexed yields (line_number, obj) starting at 1."""
        data = SAMPLE_JSONL_STR.encode("utf-8")
        results = list(json_io.jsonl_load_bytes_indexed(data))
        assert results[0] == (1, {"a": 1})
        assert len(results) == 3

    def test_jsonl_load_bytes_skips_blank_lines(self) -> None:
        """Blank byte lines are skipped."""
        data = SAMPLE_JSONL_WITH_BLANKS.encode("utf-8")
        results = list(json_io.jsonl_load_bytes(data))
        assert results == [{"a": 1}, {"b": 2}]


class TestJsonlFilePath:
    """Tests for JSONL file-based load/dump operations."""

    def test_jsonl_load_path_yields_objects(self, sde_jsonl_dir: Path) -> None:
        """jsonl_load_path yields objects from a real JSONL file."""
        path = sde_jsonl_dir / "agentTypes.jsonl"
        results = list(json_io.jsonl_load_path(path))
        assert len(results) == 3
        assert all(isinstance(r, dict) for r in results)

    def test_jsonl_load_path_indexed_starts_at_one(self, sde_jsonl_dir: Path) -> None:
        """Line numbers from jsonl_load_path_indexed start at 1."""
        path = sde_jsonl_dir / "agentTypes.jsonl"
        results = list(json_io.jsonl_load_path_indexed(path))
        assert results[0][0] == 1

    def test_jsonl_dump_path_round_trip(self, tmp_path: Path) -> None:
        """Objects survive a jsonl_dump_path → jsonl_load_path round-trip."""
        objs: list[dict[str, object]] = [{"id": 1}, {"id": 2}, {"id": 3}]
        fp = tmp_path / "out.jsonl"
        json_io.jsonl_dump_path(iter(objs), filepath=fp)
        restored = list(json_io.jsonl_load_path(fp))
        assert restored == objs

    def test_jsonl_dump_path_raises_when_file_exists_no_overwrite(
        self, tmp_path: Path
    ) -> None:
        """FileExistsError is raised when target exists and overwrite=False."""
        fp = tmp_path / "dup.jsonl"
        json_io.jsonl_dump_path(iter([{"x": 1}]), filepath=fp)
        with pytest.raises(FileExistsError):
            json_io.jsonl_dump_path(iter([{"x": 2}]), filepath=fp, overwrite=False)

    def test_jsonl_dump_path_overwrites_when_requested(self, tmp_path: Path) -> None:
        """Existing file is replaced when overwrite=True."""
        fp = tmp_path / "ow.jsonl"
        json_io.jsonl_dump_path(iter([{"v": 1}]), filepath=fp)
        json_io.jsonl_dump_path(iter([{"v": 99}]), filepath=fp, overwrite=True)
        restored = list(json_io.jsonl_load_path(fp))
        assert restored == [{"v": 99}]

    def test_jsonl_dump_path_appends_when_append_true(self, tmp_path: Path) -> None:
        """Existing file content is preserved when append=True."""
        fp = tmp_path / "append.jsonl"
        json_io.jsonl_dump_path(iter([{"v": 1}]), filepath=fp)
        json_io.jsonl_dump_path(iter([{"v": 2}]), filepath=fp, append=True)
        restored = list(json_io.jsonl_load_path(fp))
        assert restored == [{"v": 1}, {"v": 2}]

    def test_jsonl_dump_path_raises_on_indent_kwarg(self, tmp_path: Path) -> None:
        """ValueError is raised when indent keyword argument is passed."""
        fp = tmp_path / "bad.jsonl"
        with pytest.raises(ValueError, match="indent"):
            json_io.jsonl_dump_path(iter([{"v": 1}]), filepath=fp, indent=2)

    def test_jsonl_dump_path_raises_on_overwrite_and_append(
        self, tmp_path: Path
    ) -> None:
        """ValueError is raised when both overwrite and append are True."""
        fp = tmp_path / "conflict.jsonl"
        with pytest.raises(ValueError):
            json_io.jsonl_dump_path(
                iter([{"v": 1}]), filepath=fp, overwrite=True, append=True
            )


class TestJsonlDumpsAndDumpBytes:
    """Tests for jsonl_dumps and jsonl_dump_bytes helpers."""

    def test_jsonl_dumps_returns_string(self) -> None:
        """jsonl_dumps returns a newline-delimited string."""
        result = json_io.jsonl_dumps(iter([{"a": 1}, {"b": 2}]))
        lines = [l for l in result.splitlines() if l.strip()]
        assert len(lines) == 2

    def test_jsonl_dump_bytes_returns_bytes(self) -> None:
        """jsonl_dump_bytes returns bytes."""
        result = json_io.jsonl_dump_bytes(iter([{"a": 1}]))
        assert isinstance(result, bytes)

    def test_jsonl_dumps_round_trip(self) -> None:
        """jsonl_dumps → jsonl_loads round-trip preserves objects."""
        objs: list[dict[str, int]] = [{"x": i} for i in range(4)]
        serialized = json_io.jsonl_dumps(iter(objs))
        restored = list(json_io.jsonl_loads(serialized))
        assert restored == objs
