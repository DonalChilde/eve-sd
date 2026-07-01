"""Helper functions and classes for ESD CLI commands."""

from enum import StrEnum
from typing import cast

import typer

from eve_static_data.settings import EveStaticDataSettings


def get_esd_settings_from_context(ctx: typer.Context) -> EveStaticDataSettings:
    """Get the EveStaticDataSettings instance from the Typer context."""
    if ctx.obj is None or "esd-settings" not in ctx.obj:
        raise ValueError("ESD settings not found in context.")
    return cast(EveStaticDataSettings, ctx.obj["esd-settings"])


class ReportChoice(StrEnum):
    """Enumeration of report types for schema reporting output."""

    JSON = "json"
    MARKDOWN = "markdown"
    NONE = "none"
