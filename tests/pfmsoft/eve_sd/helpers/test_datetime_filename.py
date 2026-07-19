"""Tests for eve_sd.helpers.datetime_filename."""

from datetime import datetime, timezone

from pfmsoft.eve_sd.helpers.datetime_filename import (
    file_safe_datetime_string,
    file_safe_iso_datetime_string,
)


class TestFileSafeIsoDatetimeString:
    """Tests for file_safe_iso_datetime_string."""

    def test_replaces_colons_with_underscores(self) -> None:
        """Colons in the ISO string are replaced with underscores."""
        result = file_safe_iso_datetime_string("2025-07-17T14:54:23")
        assert ":" not in result
        assert result == "2025-07-17T14_54_23"

    def test_replaces_dots_with_underscores(self) -> None:
        """Dots in the ISO string are replaced with underscores."""
        result = file_safe_iso_datetime_string("2025-07-17T14:54:23.222827")
        assert "." not in result
        assert "222827" in result

    def test_replaces_plus_with_p(self) -> None:
        """Plus signs in the ISO string are replaced with 'P'."""
        result = file_safe_iso_datetime_string("2025-07-17T14:54:23+00:00")
        assert "+" not in result
        assert "P" in result

    def test_full_utc_offset_example(self) -> None:
        """Full conversion matches documented example format."""
        result = file_safe_iso_datetime_string("2025-07-17T14:54:23.222827+00:00")
        assert result == "2025-07-17T14_54_23_222827P00_00"

    def test_already_safe_string_unchanged(self) -> None:
        """A string with no special characters is returned unchanged."""
        safe = "2025-07-17T14_54_23"
        assert file_safe_iso_datetime_string(safe) == safe


class TestFileSafeDatetimeString:
    """Tests for file_safe_datetime_string."""

    def test_naive_datetime_has_no_special_chars(self) -> None:
        """Naive datetime produces a string with no ':', '.', or '+' characters."""
        dt = datetime(2025, 7, 17, 14, 54, 23, 222827)
        result = file_safe_datetime_string(dt)
        assert ":" not in result
        assert "." not in result
        assert "+" not in result

    def test_aware_utc_datetime(self) -> None:
        """UTC-aware datetime replaces '+' with 'P'."""
        dt = datetime(2025, 7, 17, 14, 54, 23, tzinfo=timezone.utc)
        result = file_safe_datetime_string(dt)
        assert "+" not in result
        assert "P" in result

    def test_microseconds_replaced(self) -> None:
        """Microsecond dot separator is replaced with underscore."""
        dt = datetime(2025, 7, 17, 14, 54, 23, 1234)
        result = file_safe_datetime_string(dt)
        assert "." not in result
        assert "1234" in result

    def test_result_is_string(self) -> None:
        """Return value is a str."""
        dt = datetime(2025, 1, 1)
        assert isinstance(file_safe_datetime_string(dt), str)
