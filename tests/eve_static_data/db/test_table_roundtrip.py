"""Round-trip tests for SQL table create/insert/retrieve flows.

Each case validates fixture data against a YAML RootModel, creates schema tables,
inserts records, and fetches them back as pydantic dataclass models.
"""

import importlib.resources
import sqlite3
from collections.abc import Callable, Iterable
from dataclasses import asdict, dataclass
from importlib.resources.abc import Traversable
from typing import Any

import pytest
import yaml
from pydantic import RootModel
from rich.pretty import pprint as rich_print

from eve_static_data.db import insert_records, request_records
from eve_static_data.models.yaml_format import yaml_datasets_root, yaml_records


@dataclass(frozen=True)
class RoundTripCase:
    """Configuration for one dataset round-trip test case."""

    case_id: str
    fixture_file_name: str
    sql_file_name: str
    root_model: type[RootModel[Any]]
    insert_func: Callable[[sqlite3.Cursor, Any], None]
    retrieve_func: Callable[[sqlite3.Cursor], Iterable[Any]]
    key_field: str


def _yaml_fixture_path(file_name: str) -> Traversable:
    """Get a Traversable path to a YAML fixture file."""
    return importlib.resources.files("tests.resources.sde_data.yaml") / file_name


def _sql_table_def_path(file_name: str) -> Traversable:
    """Get a Traversable path to a table SQL definition file."""
    return importlib.resources.files("eve_static_data.db.table_sql") / file_name


def _load_yaml_mapping(file_name: str) -> dict[Any, Any]:
    """Load a YAML mapping fixture from tests/resources."""
    fixture_path = _yaml_fixture_path(file_name)
    with fixture_path.open(encoding="utf-8") as file_handle:
        loaded: dict[Any, Any] = yaml.safe_load(file_handle)

    assert isinstance(loaded, dict)
    return loaded


def _load_sql_script(file_name: str) -> str:
    """Load a SQL schema script from src/eve_static_data/db/table_sql."""
    sql_path = _sql_table_def_path(file_name)
    with sql_path.open(encoding="utf-8") as file_handle:
        return file_handle.read()


def _expected_rows_by_key(records: Any, key_field: str) -> dict[int, dict[str, Any]]:
    """Build expected rows keyed by primary key field."""
    expected: dict[int, dict[str, Any]] = {}

    for key, record in records.root.items():
        row = asdict(record)
        row[key_field] = key
        expected[key] = row

    return expected


def _actual_rows_by_key(
    cursor: sqlite3.Cursor,
    retrieve_func: Callable[[sqlite3.Cursor], Iterable[Any]],
    key_field: str,
) -> dict[int, dict[str, Any]]:
    """Build retrieved rows keyed by primary key field."""
    actual: dict[int, dict[str, Any]] = {}

    for record in retrieve_func(cursor):
        row = asdict(record)
        actual[row[key_field]] = row

    return actual


ROUND_TRIP_CASES: list[RoundTripCase] = [
    RoundTripCase(
        case_id="agent_types",
        fixture_file_name="agentTypes.yaml",
        sql_file_name="agent-types.sql",
        root_model=yaml_datasets_root.AgentTypesRoot,
        insert_func=insert_records.agent_types,
        retrieve_func=request_records.agent_types,
        key_field="agent_types_id",
    ),
    RoundTripCase(
        case_id="agents_in_space",
        fixture_file_name="agentsInSpace.yaml",
        sql_file_name="agents-in-space.sql",
        root_model=yaml_datasets_root.AgentsInSpaceRoot,
        insert_func=insert_records.agents_in_space,
        retrieve_func=request_records.agents_in_space,
        key_field="agents_in_space_id",
    ),
    RoundTripCase(
        case_id="ancestries",
        fixture_file_name="ancestries.yaml",
        sql_file_name="ancestries.sql",
        root_model=yaml_datasets_root.AncestriesRoot,
        insert_func=insert_records.ancestries,
        retrieve_func=request_records.ancestries,
        key_field="ancestries_id",
    ),
    RoundTripCase(
        case_id="bloodlines",
        fixture_file_name="bloodlines.yaml",
        sql_file_name="bloodlines.sql",
        root_model=yaml_datasets_root.BloodlinesRoot,
        insert_func=insert_records.bloodlines,
        retrieve_func=request_records.bloodlines,
        key_field="bloodlines_id",
    ),
    RoundTripCase(
        case_id="blueprints",
        fixture_file_name="blueprints.yaml",
        sql_file_name="blueprints.sql",
        root_model=yaml_datasets_root.BlueprintsRoot,
        insert_func=insert_records.blueprints,
        retrieve_func=request_records.blueprints,
        key_field="blueprints_id",
    ),
    RoundTripCase(
        case_id="categories",
        fixture_file_name="categories.yaml",
        sql_file_name="categories.sql",
        root_model=yaml_datasets_root.CategoriesRoot,
        insert_func=insert_records.categories,
        retrieve_func=request_records.categories,
        key_field="categories_id",
    ),
    RoundTripCase(
        case_id="certificates",
        fixture_file_name="certificates.yaml",
        sql_file_name="certificates.sql",
        root_model=yaml_datasets_root.CertificatesRoot,
        insert_func=insert_records.certificates,
        retrieve_func=request_records.certificates,
        key_field="certificates_id",
    ),
]


@pytest.mark.parametrize("case", ROUND_TRIP_CASES, ids=lambda case: case.case_id)
def test_table_round_trip_for_yaml_dataset(case: RoundTripCase) -> None:
    """Create table, insert validated records, and retrieve the same records."""
    payload = _load_yaml_mapping(case.fixture_file_name)
    validated_records = case.root_model.model_validate(payload)

    connection = sqlite3.connect(":memory:")
    connection.executescript(_load_sql_script(case.sql_file_name))
    with connection:
        cursor = connection.cursor()

        case.insert_func(cursor, validated_records)

        expected = _expected_rows_by_key(validated_records, case.key_field)
        actual = _actual_rows_by_key(cursor, case.retrieve_func, case.key_field)

    expected_keys = set(expected.keys())
    actual_keys = set(actual.keys())
    assert expected_keys == actual_keys, (
        f"Expected keys {expected_keys} do not match actual keys {actual_keys}"
    )
    for key in expected_keys:
        expected_row = expected[key]
        actual_row = actual[key]
        assert expected_row == actual_row, (
            f"Row for key {key} does not match expected.\nExpected: {expected_row}\nActual: {actual_row}"
        )

    # assert actual == expected

    # TODO try a version where the root model is compared against the retrieved records.
    # This will require transforming the retrieved records back into the root model structure,
    # making a dict using the key field, and setting the keyfield to None on the retrieved records.
    # This should make equivalent structures and data.
