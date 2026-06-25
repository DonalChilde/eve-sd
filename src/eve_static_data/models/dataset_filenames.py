"""This module defines the SdeDatasets enum, which contains the names of all the dataset files in the SDE."""

from enum import StrEnum


class SdeDatasets(StrEnum):
    AGENTS_IN_SPACE = "agentsInSpace"
    AGENT_TYPES = "agentTypes"
    ANCESTRIES = "ancestries"
    ARCHETYPES = "archetypes"
    BLOODLINES = "bloodlines"
    BLUEPRINTS = "blueprints"
    CATEGORIES = "categories"
    CERTIFICATES = "certificates"
    CHARACTER_ATTRIBUTES = "characterAttributes"
    CHARACTER_TITLES = "characterTitles"
    CLONE_GRADES = "cloneGrades"
    COMPRESSIBLE_TYPES = "compressibleTypes"
    CONTRABAND_TYPES = "contrabandTypes"
    CONTROL_TOWER_RESOURCES = "controlTowerResources"
    CORPORATION_ACTIVITIES = "corporationActivities"
    DBUFF_COLLECTIONS = "dbuffCollections"
    DOGMA_ATTRIBUTE_CATEGORIES = "dogmaAttributeCategories"
    DOGMA_ATTRIBUTES = "dogmaAttributes"
    DOGMA_EFFECTS = "dogmaEffects"
    DOGMA_UNITS = "dogmaUnits"
    DUNGEONS = "dungeons"
    DYNAMIC_ITEM_ATTRIBUTES = "dynamicItemAttributes"
    FACTIONS = "factions"
    FREELANCE_JOB_SCHEMAS = "freelanceJobSchemas"
    GRAPHICS = "graphics"
    GROUPS = "groups"
    ICONS = "icons"
    LANDMARKS = "landmarks"
    MAP_ASTEROID_BELTS = "mapAsteroidBelts"
    MAP_CONSTELLATIONS = "mapConstellations"
    MAP_MOONS = "mapMoons"
    MAP_PLANETS = "mapPlanets"
    MAP_REGIONS = "mapRegions"
    MAP_SECONDARY_SUNS = "mapSecondarySuns"
    MAP_SOLAR_SYSTEMS = "mapSolarSystems"
    MAP_STARGATES = "mapStargates"
    MAP_STARS = "mapStars"
    MARKET_GROUPS = "marketGroups"
    MASTERIES = "masteries"
    META_GROUPS = "metaGroups"
    MERCENARY_TACTICAL_OPERATIONS = "mercenaryTacticalOperations"
    NPC_CHARACTERS = "npcCharacters"
    NPC_CORPORATION_DIVISIONS = "npcCorporationDivisions"
    NPC_CORPORATIONS = "npcCorporations"
    NPC_STATIONS = "npcStations"
    PLANET_RESOURCES = "planetResources"
    PLANET_SCHEMATICS = "planetSchematics"
    RACES = "races"
    SDE_INFO = "_sde"
    SKIN_LICENSES = "skinLicenses"
    SKIN_MATERIALS = "skinMaterials"
    SKINS = "skins"
    SOVEREIGNTY_UPGRADES = "sovereigntyUpgrades"
    STATION_OPERATIONS = "stationOperations"
    STATION_SERVICES = "stationServices"
    TRANSLATION_LANGUAGES = "translationLanguages"
    TYPE_BONUS = "typeBonus"
    TYPE_DOGMA = "typeDogma"
    TYPE_LISTS = "typeLists"
    TYPE_MATERIALS = "typeMaterials"
    TYPES = "types"

    def as_jsonl(self) -> str:
        """Return the filename for the JSONL version of this file name.

        This file name is used when working with the original SDE dataset files, which are in JSONL format.
        """
        return f"{self.value}.jsonl"

    def as_json(self) -> str:
        """Return the filename for the JSON version of this file name.

        This file name is used when exporting the dataset to JSON format, as opposed to
        the original JSONL or YAML format used in the SDE.
        """
        return f"{self.value}.json"

    def as_yaml(self) -> str:
        """Return the filename for the YAML version of this file name.

        This file name is used when working with the original SDE dataset files, which are in YAML format.
        """
        return f"{self.value}.yaml"
