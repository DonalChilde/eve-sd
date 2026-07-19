"""Tests for eve_sd.helpers.save_text_file."""

from pathlib import Path

import pytest

from pfmsoft.eve_sd.helpers.save_text_file import save_text_file


class TestSaveTextFile:
    """Tests for save_text_file."""

    def test_creates_file_with_content(self, tmp_path: Path) -> None:
        """File is created and contains the given text."""
        result = save_text_file(
            text="hello world", output_directory=tmp_path, file_name="out.txt"
        )
        assert result.read_text(encoding="utf-8") == "hello world"

    def test_returns_path_to_written_file(self, tmp_path: Path) -> None:
        """Return value is the path to the written file."""
        result = save_text_file(
            text="x", output_directory=tmp_path, file_name="result.txt"
        )
        assert result == tmp_path / "result.txt"
        assert result.exists()

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Missing parent directories are created automatically."""
        deep = tmp_path / "a" / "b" / "c"
        save_text_file(text="nested", output_directory=deep, file_name="file.txt")
        assert (deep / "file.txt").exists()

    def test_raises_file_exists_error_when_file_exists_and_no_overwrite(
        self, tmp_path: Path
    ) -> None:
        """FileExistsError is raised when the target exists and overwrite=False."""
        save_text_file(text="first", output_directory=tmp_path, file_name="dup.txt")
        with pytest.raises(FileExistsError):
            save_text_file(
                text="second",
                output_directory=tmp_path,
                file_name="dup.txt",
                overwrite=False,
            )

    def test_overwrites_existing_file_when_overwrite_true(self, tmp_path: Path) -> None:
        """Existing file content is replaced when overwrite=True."""
        save_text_file(text="first", output_directory=tmp_path, file_name="ow.txt")
        save_text_file(
            text="second",
            output_directory=tmp_path,
            file_name="ow.txt",
            overwrite=True,
        )
        assert (tmp_path / "ow.txt").read_text(encoding="utf-8") == "second"

    def test_writes_unicode_content(self, tmp_path: Path) -> None:
        """Unicode text is written and read back correctly."""
        text = "日本語テスト — éàü"
        save_text_file(text=text, output_directory=tmp_path, file_name="unicode.txt")
        assert (tmp_path / "unicode.txt").read_text(encoding="utf-8") == text
