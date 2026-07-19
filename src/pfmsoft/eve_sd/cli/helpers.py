"""Shared helpers for eve-sd CLI commands."""

from enum import StrEnum
from typing import cast

import typer

from pfmsoft.eve_sd.settings import EveSDSettings


def get_esd_settings_from_context(ctx: typer.Context) -> EveSDSettings:
    """Get the EveStaticDataSettings instance from the Typer context."""
    if ctx.obj is None or "esd-settings" not in ctx.obj:
        raise ValueError("ESD settings not found in context.")
    return cast(EveSDSettings, ctx.obj["esd-settings"])


class ReportChoice(StrEnum):
    """Enumeration of report types for schema reporting output."""

    JSON = "json"
    MARKDOWN = "markdown"
    NONE = "none"
