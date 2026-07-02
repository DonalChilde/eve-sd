#!/usr/bin/env python3
"""
Generate src/eve_static_data/db/table_defs.py.

Run from project root:
    .venv/bin/python scripts/gen_table_defs.py > src/eve_static_data/db/table_defs.py
"""

from __future__ import annotations

import re
import sys
import types as _types
from dataclasses import fields, is_dataclass
from typing import Any, Union, get_args, get_origin, get_type_hints

sys.path.insert(0, "src")

from eve_sd.models import records
from eve_sd.models.records import LocalizedString

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def snake_case(name: str) -> str:
    s = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
    s = s.lower()
    s = re.sub(r"__+", "_", s)  # collapse consecutive underscores from embedded _
    return s


def unwrap_optional(ann: Any) -> Any:
    """Return the inner type if ann is Optional[T], else return ann."""
    args = get_args(ann)
    # Python 3.10+ `X | None`  →  types.UnionType
    if isinstance(ann, _types.UnionType):
        non_none = [a for a in args if a is not type(None)]
        if len(non_none) == 1:
            return non_none[0]
    # typing.Union / typing.Optional
    if get_origin(ann) is Union:
        non_none = [a for a in args if a is not type(None)]
        if len(non_none) == 1:
            return non_none[0]
    return ann


def is_localized(ann: Any) -> bool:
    return unwrap_optional(ann) is LocalizedString


def is_list_field(ann: Any) -> bool:
    return get_origin(unwrap_optional(ann)) is list


def py_to_sqlite(ann: Any) -> str:
    base = unwrap_optional(ann)
    if base is bool or base is int:
        return "INTEGER"
    if base is float:
        return "REAL"
    if base is str:
        return "TEXT"
    return "JSON"


def is_top_level(cls: Any) -> bool:
    """Top-level dataset classes have a 'key' field and belong to records module."""
    if not (isinstance(cls, type) and is_dataclass(cls)):
        return False
    if cls.__module__ != records.__name__:
        return False
    return "key" in {f.name for f in fields(cls)}


# ---------------------------------------------------------------------------
# Per-dataset DDL builder
# ---------------------------------------------------------------------------


def build_dataset(cls: type) -> tuple[list[str], list[str]]:
    """Return (create_stmts, index_stmts) for a top-level dataset class."""
    table = snake_case(cls.__name__)
    hints = get_type_hints(cls)
    flds = fields(cls)

    main_cols: list[str] = ["    id INTEGER PRIMARY KEY AUTOINCREMENT"]
    loc_fields: list[str] = []
    list_fields: list[str] = []

    for f in flds:
        sname = snake_case(f.name)
        ann = hints.get(f.name, Any)

        if f.name == "key":
            main_cols.append("    source_key INTEGER")
        elif is_localized(ann):
            loc_fields.append(sname)
        elif is_list_field(ann):
            list_fields.append(sname)
        else:
            main_cols.append(f"    {sname} {py_to_sqlite(ann)}")

    create_stmts: list[str] = []
    index_stmts: list[str] = []

    # ── main table ──────────────────────────────────────────────────────────
    cols_str = ",\n".join(main_cols)
    create_stmts.append(f"CREATE TABLE IF NOT EXISTS {table} (\n{cols_str});")
    index_stmts.append(
        f"CREATE INDEX IF NOT EXISTS idx_{table}_source_key ON {table} (source_key);"
    )

    # ── consolidated localized table ─────────────────────────────────────────
    if loc_fields:
        loc_table = f"{table}_localized"
        loc_cols = [
            "    id INTEGER PRIMARY KEY AUTOINCREMENT",
            "    parent_id INTEGER NOT NULL",
            "    source_key INTEGER",
            "    language TEXT",
        ] + [f"    {lf} TEXT" for lf in loc_fields]
        loc_cols_str = ",\n".join(loc_cols)
        create_stmts.append(
            f"CREATE TABLE IF NOT EXISTS {loc_table} (\n{loc_cols_str});"
        )
        index_stmts.append(
            f"CREATE INDEX IF NOT EXISTS idx_{loc_table}_parent_id"
            f" ON {loc_table} (parent_id);"
        )
        index_stmts.append(
            f"CREATE INDEX IF NOT EXISTS idx_{loc_table}_language"
            f" ON {loc_table} (language);"
        )

    # ── junction tables for list fields ────────────────────────────────────
    for lf in list_fields:
        jt = f"{table}_{lf}"
        jt_cols = ",\n".join([
            "    id INTEGER PRIMARY KEY AUTOINCREMENT",
            "    parent_id INTEGER NOT NULL",
            "    item_index INTEGER NOT NULL",
            "    item_json JSON",
        ])
        create_stmts.append(f"CREATE TABLE IF NOT EXISTS {jt} (\n{jt_cols});")
        index_stmts.append(
            f"CREATE INDEX IF NOT EXISTS idx_{jt}_parent_id ON {jt} (parent_id);"
        )
        index_stmts.append(
            f"CREATE INDEX IF NOT EXISTS idx_{jt}_item_index ON {jt} (item_index);"
        )

    return create_stmts, index_stmts


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    # Collect & sort top-level dataset classes alphabetically by table name
    top_level = sorted(
        [
            (snake_case(name), name, cls)
            for name, cls in vars(records).items()
            if is_top_level(cls)
        ],
        key=lambda t: t[0],
    )

    lines: list[str] = [
        '"""Static SQLite DDL statements for EVE SDE tables."""',
        "",
    ]

    all_create: list[str] = []
    all_index: list[str] = []

    for table_name, cls_name, cls in top_level:
        var_name = table_name.upper() + "_TABLE"
        create_stmts, index_stmts = build_dataset(cls)
        all_create.extend(create_stmts)
        all_index.extend(index_stmts)

        # ── per-dataset string variable ────────────────────────────────────
        combined_ddl = "\n".join(create_stmts)
        lines.append(f'{var_name}: str = """')
        lines.append(combined_ddl)
        lines.append('"""')
        lines.append("")

    # ── CREATE_TABLE_STATEMENTS tuple ────────────────────────────────────────
    lines.append("CREATE_TABLE_STATEMENTS: tuple[str, ...] = (")
    for stmt in all_create:
        # Use single-quoted strings to avoid escaping issues
        escaped = stmt.replace("\\", "\\\\")
        lines.append(f"    {repr(stmt)},")
    lines.append(")")
    lines.append("")

    # ── CREATE_INDEX_STATEMENTS tuple ────────────────────────────────────────
    lines.append("CREATE_INDEX_STATEMENTS: tuple[str, ...] = (")
    for stmt in all_index:
        lines.append(f"    {repr(stmt)},")
    lines.append(")")
    lines.append("")

    # ── CREATE_SCHEMA_STATEMENTS ─────────────────────────────────────────────
    lines.append(
        "CREATE_SCHEMA_STATEMENTS: tuple[str, ...] = ("
        "*CREATE_TABLE_STATEMENTS, *CREATE_INDEX_STATEMENTS)"
    )
    lines.append("")

    print("\n".join(lines))


if __name__ == "__main__":
    main()
