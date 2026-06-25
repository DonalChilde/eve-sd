"""Functions to insert validated records from pydantic rootmodels."""

import sqlite3

import eve_static_data.models.yaml_format.yaml_datasets_root
from eve_static_data.models.common import (
    ACTIVITIES,
    Lang,
    LocalizableRecord,
    PossibleTranslationLanguages,
)
from eve_static_data.models.yaml_format import yaml_datasets_root
from eve_static_data.models.yaml_format import yaml_records as yaml_records


def _langs_in_record(record: LocalizableRecord) -> set[Lang]:
    """Get the set of languages that have localized fields in the record.

    This is to support inserting localized fields for records that are only localized in
    a subset of languages. This might happen when the records are preprocessed to contain
    only one language, or when the records are missing localized fields in some languages.
    """
    language_fields = record.localized_fields("en").keys()
    languages: set[Lang] = set()
    for field in language_fields:
        languages.update(getattr(record, field).keys())
    return languages.intersection(PossibleTranslationLanguages)


def agent_types(
    cursor: sqlite3.Cursor, records: yaml_datasets_root.AgentTypesRoot
) -> None:
    """Insert records into the agent_types table."""
    for agent_types_id, record in records.root.items():
        cursor.execute(
            "INSERT INTO agent_types (agent_types_id, agent_name) VALUES (?, ?);",
            (agent_types_id, record.name),
        )


def agents_in_space(
    cursor: sqlite3.Cursor,
    records: eve_static_data.models.yaml_format.yaml_datasets_root.AgentsInSpaceRoot,
) -> None:
    """Insert records into the agents_in_space table."""
    for agents_in_space_id, record in records.root.items():
        cursor.execute(
            "INSERT INTO agents_in_space (agents_in_space_id, dungeonID, solarSystemID, spawnPointID, typeID) VALUES (?, ?, ?, ?, ?);",
            (
                agents_in_space_id,
                record.dungeonID,
                record.solarSystemID,
                record.spawnPointID,
                record.typeID,
            ),
        )


def ancestries(
    cursor: sqlite3.Cursor, records: yaml_datasets_root.AncestriesRoot
) -> None:
    """Insert records into the ancestries table."""
    for ancestries_id, record in records.root.items():
        cursor.execute(
            "INSERT INTO ancestries (ancestries_id, bloodlineID, charisma, iconID, intelligence, memory, perception, shortDescription, willpower) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);",
            (
                ancestries_id,
                record.bloodlineID,
                record.charisma,
                record.iconID,
                record.intelligence,
                record.memory,
                record.perception,
                record.shortDescription,
                record.willpower,
            ),
        )

        for lang in _langs_in_record(record):
            localized = record.localized_fields(lang)
            cursor.execute(
                "INSERT INTO ancestries_localized (ancestries_id, lang, localized_name, localized_description) VALUES (?, ?, ?, ?);",
                (
                    ancestries_id,
                    lang,
                    localized["name"],
                    localized["description"],
                ),
            )


def bloodlines(
    cursor: sqlite3.Cursor, records: yaml_datasets_root.BloodlinesRoot
) -> None:
    """Insert records into the bloodlines table."""
    for bloodlines_id, record in records.root.items():
        cursor.execute(
            "INSERT INTO bloodlines (bloodlines_id, charisma, corporationID, iconID, intelligence, memory, perception, raceID, willpower) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);",
            (
                bloodlines_id,
                record.charisma,
                record.corporationID,
                record.iconID,
                record.intelligence,
                record.memory,
                record.perception,
                record.raceID,
                record.willpower,
            ),
        )
        for lang in _langs_in_record(record):
            localized = record.localized_fields(lang)
            cursor.execute(
                "INSERT INTO bloodlines_localized (bloodlines_id, lang, localized_name, localized_description) VALUES (?, ?, ?, ?);",
                (
                    bloodlines_id,
                    lang,
                    localized["name"],
                    localized["description"],
                ),
            )


def blueprints(
    cursor: sqlite3.Cursor, records: yaml_datasets_root.BlueprintsRoot
) -> None:
    """Insert records into the blueprints table."""
    for blueprints_id, record in records.root.items():
        cursor.execute(
            "INSERT INTO blueprints (blueprints_id, blueprintTypeID, maxProductionLimit) VALUES (?, ?, ?);",
            (
                blueprints_id,
                record.blueprintTypeID,
                record.maxProductionLimit,
            ),
        )
        for activity_name in ACTIVITIES:
            activity_value: yaml_records.Blueprints_Activity | None = getattr(
                record.activities, activity_name
            )
            if activity_value is not None:
                cursor.execute(
                    "INSERT INTO blueprint_activities (blueprint_id, activity_type, activity_time) VALUES (?, ?, ?);",
                    (blueprints_id, activity_name, activity_value.time),
                )
                last_inserted_id = cursor.lastrowid
                if activity_value.materials is not None:
                    for material in activity_value.materials:
                        cursor.execute(
                            "INSERT INTO blueprint_activity_materials (blueprint_activity_id, typeID, quantity) VALUES (?, ?, ?);",
                            (last_inserted_id, material.typeID, material.quantity),
                        )
                if activity_value.products is not None:
                    for product in activity_value.products:
                        cursor.execute(
                            "INSERT INTO blueprint_activity_products (blueprint_activity_id, typeID, quantity, probability) VALUES (?, ?, ?, ?);",
                            (
                                last_inserted_id,
                                product.typeID,
                                product.quantity,
                                product.probability,
                            ),
                        )
                if activity_value.skills is not None:
                    for skill in activity_value.skills:
                        cursor.execute(
                            "INSERT INTO blueprint_activity_skills (blueprint_activity_id, typeID, skill_level) VALUES (?, ?, ?);",
                            (last_inserted_id, skill.typeID, skill.level),
                        )


def categories(
    cursor: sqlite3.Cursor, records: yaml_datasets_root.CategoriesRoot
) -> None:
    """Insert records into the categories table."""
    for categories_id, record in records.root.items():
        cursor.execute(
            "INSERT INTO categories (categories_id, iconID,published) VALUES (?, ?, ?);",
            (categories_id, record.iconID, record.published),
        )
        for lang in _langs_in_record(record):
            localized = record.localized_fields(lang)
            cursor.execute(
                "INSERT INTO categories_localized (categories_id, lang, localized_name) VALUES (?, ?, ?);",
                (
                    categories_id,
                    lang,
                    localized["name"],
                ),
            )


def certificates(
    cursor: sqlite3.Cursor, records: yaml_datasets_root.CertificatesRoot
) -> None:
    """Insert records into the certificates table."""
    for certificates_id, record in records.root.items():
        cursor.execute(
            "INSERT INTO certificates (certificates_id, groupID) VALUES (?, ?);",
            (certificates_id, record.groupID),
        )
        for lang in _langs_in_record(record):
            localized = record.localized_fields(lang)
            cursor.execute(
                "INSERT INTO certificates_localized (certificates_id, lang, localized_name,localized_description) VALUES (?, ?, ?, ?);",
                (
                    certificates_id,
                    lang,
                    localized["name"],
                    localized["description"],
                ),
            )
        if record.recommendedFor:
            values = [(certificates_id, value) for value in record.recommendedFor]
            cursor.executemany(
                "INSERT INTO certificates_recommended_for (certificates_id, value_int) VALUES (?, ?);",
                values,
            )
        if record.skillTypes:
            for skill_type_id, skill_lvls in record.skillTypes.items():
                cursor.execute(
                    "INSERT INTO certificates_skill_type (certificates_skill_type_id,certificates_id, basic_lvl, standard_lvl, improved_lvl, advanced_lvl, elite_lvl) VALUES (?, ?, ?, ?, ?, ?, ?);",
                    (
                        skill_type_id,
                        certificates_id,
                        skill_lvls.basic,
                        skill_lvls.standard,
                        skill_lvls.improved,
                        skill_lvls.advanced,
                        skill_lvls.elite,
                    ),
                )
