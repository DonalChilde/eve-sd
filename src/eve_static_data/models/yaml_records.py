"""Dataclass models for the records in YAML format SDE datasets.

Prefer the use of the yaml format datamodels over the jsonl format datamodels,
because the yaml format datamodels are easier to reason with and provide better inherant
structure guarantees.

Also, yaml allows integer keys in mappings, which is a common pattern in the SDE datasets,
and json does not.

Because pyyaml is SO SLOW, consider exporting the raw yaml data to json one time, and
loading through pydantic root models to handle the type conversion of the dict keys from
string to int. The speedup is 60x on my machine.

When loading with pydantic, the top level dict keys do not get stored in the record model,
as the root model is defined as dict[int, <record model>]. This means that the individual
record models do not have acess to their own key without further steps. When serializing
to the database, the key is added to the record as a field, and when deserializing from
the database, the key field is set in the record. This would allows the same models to be
used for YAML/JSON datasets and database records.

Records with LocalizedString fields support LocalizedRecord, which provides a
localized_fields method to return a dict of the localized fields in the model for a given
language.

This will allow the same data model to be used to load ans save a subset of avaliable
languages. For example, if only English and German are needed, The SDE files can be processed
to only include those languages.




Some specific datasets may required a more complex database return model. Right now they are
defined as types instead of dataclasses.
"""

from dataclasses import dataclass
from typing import Any, Literal

from eve_static_data.models.common import (
    TRANSLATION_MISSING,
    Lang,
    LocalizableRecord,
    LocalizedString,
    lang_check,
)

# ------------------------------------------------------------------------------
# Common model definitions.
#     These models are used more than one time in this file.
# ------------------------------------------------------------------------------


@dataclass
class Materials:
    """Model used in multiple datasets for materials, e.g. in blueprints and typeMaterials."""

    typeID: int
    quantity: int


@dataclass
class Skills:
    """Model used in multiple datasets for skills, e.g. in blueprints and npcCharacters."""

    typeID: int
    level: int


@dataclass
class Color:
    """Model used in multiple datasets for color, e.g. in metaGroups."""

    b: float
    g: float
    r: float


@dataclass
class Position:
    """Model used in multiple datasets for position, e.g. in celestialObjects and npcCharacters."""

    x: float
    y: float
    z: float


@dataclass
class Position2D:
    """Model used in multiple datasets for 2D position, e.g. in mapSolarSystems."""

    x: float
    y: float


# ------------------------------------------------------------------------------
# File level record model definitions.
# ------------------------------------------------------------------------------


@dataclass(slots=True, kw_only=True)
class AgentsInSpace:
    """Model for the agentsInSpace.yaml dataset."""

    agents_in_space_id: int | None = None
    dungeonID: int
    solarSystemID: int
    spawnPointID: int
    typeID: int


@dataclass(slots=True, kw_only=True)
class AgentTypes:
    """Model for the agentTypes.yaml dataset."""

    agent_types_id: int | None = None
    name: str


@dataclass(slots=True, kw_only=True)
class Ancestries(LocalizableRecord):
    """Model for the ancestries.yaml dataset."""

    ancestries_id: int | None = None
    bloodlineID: int
    charisma: int
    description: LocalizedString
    iconID: int | None = None
    intelligence: int
    memory: int
    name: LocalizedString
    perception: int
    shortDescription: str | None = None
    willpower: int

    def localized_fields(
        self, lang: Lang | None
    ) -> dict[Literal["description", "name"], str | None]:
        """Returns a dict of the localized fields in the model."""
        if lang is None:
            return {"description": None, "name": None}

        return {
            "description": self.localized_description(lang),
            "name": self.localized_name(lang),
        }

    def localized_description(self, lang: Lang) -> str:
        """Returns the localized description for the given language."""
        lang_check(lang)
        return self.description.get(lang, TRANSLATION_MISSING)

    def localized_name(self, lang: Lang) -> str:
        """Returns the localized name for the given language."""
        lang_check(lang)
        return self.name.get(lang, TRANSLATION_MISSING)


@dataclass(slots=True, kw_only=True)
class Bloodlines(LocalizableRecord):
    """Model for the bloodlines.yaml dataset."""

    bloodlines_id: int | None = None
    charisma: int
    corporationID: int
    description: LocalizedString
    iconID: int | None = None
    intelligence: int
    memory: int
    name: LocalizedString
    perception: int
    raceID: int
    willpower: int

    def localized_fields(
        self, lang: Lang | None
    ) -> dict[Literal["name", "description"], str | None]:
        """Returns a dict of the localized fields in the model."""
        if lang is None:
            return {"description": None, "name": None}
        return {
            "description": self.localized_description(lang),
            "name": self.localized_name(lang),
        }

    def localized_description(self, lang: Lang) -> str:
        """Returns the localized description for the given language."""
        lang_check(lang)
        return self.description.get(lang, TRANSLATION_MISSING)

    def localized_name(self, lang: Lang) -> str:
        """Returns the localized name for the given language."""
        lang_check(lang)
        return self.name.get(lang, TRANSLATION_MISSING)


@dataclass(slots=True, kw_only=True)
class Blueprints_Products:
    """Nested model for the blueprints.yaml SDE file."""

    typeID: int
    quantity: int
    probability: float | None = None


@dataclass(slots=True, kw_only=True)
class Blueprints_Activity:
    """Nested model for the blueprints.yaml SDE file."""

    materials: list[Materials] | None = None
    skills: list[Skills] | None = None
    time: int
    products: list[Blueprints_Products] | None = None


@dataclass(slots=True, kw_only=True)
class Blueprints_Activities:
    """Nested model for the blueprints.yaml SDE file."""

    copying: Blueprints_Activity | None = None
    invention: Blueprints_Activity | None = None
    manufacturing: Blueprints_Activity | None = None
    reaction: Blueprints_Activity | None = None
    research_material: Blueprints_Activity | None = None
    research_time: Blueprints_Activity | None = None


@dataclass(slots=True, kw_only=True)
class Blueprints:
    """Model for the blueprints.yaml SDE file."""

    blueprints_id: int | None = None
    activities: Blueprints_Activities
    blueprintTypeID: int
    maxProductionLimit: int


@dataclass(slots=True, kw_only=True)
class Categories(LocalizableRecord):
    """Model for the categories.yaml SDE file."""

    categories_id: int | None = None
    name: LocalizedString
    published: bool
    iconID: int | None = None

    def localized_fields(self, lang: Lang | None) -> dict[Literal["name"], str | None]:
        """Returns a dict of the localized fields in the model."""
        if lang is None:
            return {"name": None}
        return {"name": self.localized_name(lang)}

    def localized_name(self, lang: Lang) -> str:
        """Returns the localized name for the given language."""
        lang_check(lang)
        return self.name.get(lang, TRANSLATION_MISSING)


@dataclass(slots=True, kw_only=True)
class Certificates_SkillType:
    """Nested model for the certificates.yaml SDE file."""

    basic: int
    standard: int
    improved: int
    advanced: int
    elite: int


@dataclass(slots=True, kw_only=True)
class Certificates(LocalizableRecord):
    """Model for the certificates.yaml SDE file."""

    certificates_id: int | None = None
    description: LocalizedString
    groupID: int
    name: LocalizedString
    recommendedFor: list[int] | None = None
    skillTypes: dict[int, Certificates_SkillType]

    def localized_fields(
        self, lang: Lang | None
    ) -> dict[Literal["name", "description"], str | None]:
        """Returns a dict of the localized fields in the model."""
        if lang is None:
            return {"description": None, "name": None}
        return {
            "description": self.localized_description(lang),
            "name": self.localized_name(lang),
        }

    def localized_name(self, lang: Lang) -> str:
        """Returns the localized name for the given language."""
        lang_check(lang)
        return self.name.get(lang, TRANSLATION_MISSING)

    def localized_description(self, lang: Lang) -> str:
        """Returns the localized description for the given language."""
        lang_check(lang)
        return self.description.get(lang, TRANSLATION_MISSING)


@dataclass(slots=True, kw_only=True)
class CharacterAttributes(LocalizableRecord):
    """Model for the characterAttributes.yaml SDE file."""

    character_attributes_id: int | None = None
    description: str
    iconID: int
    name: LocalizedString
    notes: str
    shortDescription: str

    def localized_fields(self, lang: Lang | None) -> dict[Literal["name"], str | None]:
        """Returns a dict of the localized fields in the model."""
        if lang is None:
            return {"name": None}
        return {"name": self.localized_name(lang)}

    def localized_name(self, lang: Lang) -> str:
        """Returns the localized name for the given language."""
        lang_check(lang)
        return self.name.get(lang, TRANSLATION_MISSING)


@dataclass(slots=True, kw_only=True)
class CloneGrades:
    """Model for the cloneGrades.yaml SDE file."""

    clone_grades_id: int | None = None
    name: str
    skills: list[Skills]


@dataclass(slots=True, kw_only=True)
class CompressibleTypes:
    """Model for the compressibleTypes.yaml SDE file."""

    compressible_types_id: int | None = None
    compressedTypeID: int


@dataclass(slots=True, kw_only=True)
class ContrabandTypes_Faction:
    """Nested model for the contrabandTypes.yaml SDE file."""

    attackMinSec: float
    confiscateMinSec: float
    fineByValue: float
    standingLoss: float


@dataclass(slots=True, kw_only=True)
class ContrabandTypes:
    """Model for the contrabandTypes.yaml SDE file."""

    contraband_types_id: int | None = None
    factions: dict[int, ContrabandTypes_Faction]


@dataclass(slots=True, kw_only=True)
class ControlTowerResources_Resource:
    """Nested model for the controlTowerResources.yaml SDE file."""

    factionID: int | None = None
    minSecurityLevel: float | None = None
    purpose: int
    quantity: int
    resourceTypeID: int


@dataclass(slots=True, kw_only=True)
class ControlTowerResources:
    """Model for the controlTowerResources.yaml SDE file."""

    control_tower_resources_id: int | None = None
    resources: list[ControlTowerResources_Resource]


@dataclass(slots=True, kw_only=True)
class CorporationActivities(LocalizableRecord):
    """Model for the corporationActivities.yaml SDE file."""

    corporation_activities_id: int | None = None
    name: LocalizedString

    def localized_fields(self, lang: Lang | None) -> dict[Literal["name"], str | None]:
        """Returns a dict of the localized fields in the model."""
        if lang is None:
            return {"name": None}
        return {"name": self.localized_name(lang)}

    def localized_name(self, lang: Lang) -> str:
        """Returns the localized name for the given language."""
        lang_check(lang)
        return self.name.get(lang, TRANSLATION_MISSING)


@dataclass(slots=True, kw_only=True)
class DebuffCollections_LocationGroupModifier:
    """Nested model for the dbuffCollections.yaml SDE file."""

    dogmaAttributeID: int
    groupID: int


@dataclass(slots=True, kw_only=True)
class DebuffCollections_LocationModifier:
    """Nested model for the dbuffCollections.yaml SDE file."""

    dogmaAttributeID: int


@dataclass(slots=True, kw_only=True)
class DebuffCollections_LocationRequiredSkillModifier:
    """Nested model for the dbuffCollections.yaml SDE file."""

    dogmaAttributeID: int
    skillID: int


@dataclass(slots=True, kw_only=True)
class DebuffCollections_ItemModifier:
    """Nested model for the dbuffCollections.yaml SDE file."""

    dogmaAttributeID: int


@dataclass(slots=True, kw_only=True)
class DebuffCollections(LocalizableRecord):
    """Model for the dbuffCollections.yaml SDE file."""

    debuff_collections_id: int | None = None
    aggregateMode: str
    developerDescription: str
    itemModifiers: list[DebuffCollections_ItemModifier] | None = None
    locationGroupModifiers: list[DebuffCollections_LocationGroupModifier] | None = None
    locationModifiers: list[DebuffCollections_LocationModifier] | None = None
    locationRequiredSkillModifiers: (
        list[DebuffCollections_LocationRequiredSkillModifier] | None
    ) = None
    operationName: str
    showOutputValueInUI: str
    displayName: LocalizedString | None = None

    def localized_fields(
        self, lang: Lang | None
    ) -> dict[Literal["displayName"], str | None]:
        """Returns a dict of the localized fields in the model."""
        if lang is None:
            return {"displayName": None}
        return {
            "displayName": self.localized_displayName(lang),
        }

    def localized_displayName(self, lang: Lang) -> str | None:
        """Returns the localized display name for the given language."""
        lang_check(lang)
        return (
            self.displayName.get(lang, TRANSLATION_MISSING)
            if self.displayName
            else None
        )


@dataclass(slots=True, kw_only=True)
class DogmaAttributeCategories:
    """Model for the dogmaAttributeCategories.yaml SDE file."""

    description: str | None = None
    name: str


@dataclass(slots=True, kw_only=True)
class DogmaAttributes(LocalizableRecord):
    """Model for the dogmaAttributes.yaml SDE file."""

    dogma_attributes_id: int | None = None
    attributeCategoryID: int | None = None
    dataType: int
    defaultValue: float
    description: str | None = None
    displayWhenZero: bool
    highIsGood: bool
    name: str
    published: bool
    stackable: bool
    displayName: LocalizedString | None = None
    iconID: int | None = None
    tooltipDescription: LocalizedString | None = None
    tooltipTitle: LocalizedString | None = None
    unitID: int | None = None
    chargeRechargeTimeID: int | None = None
    maxAttributeID: int | None = None
    minAttributeID: int | None = None

    def localized_fields(
        self, lang: Lang | None
    ) -> dict[Literal["displayName", "tooltipDescription", "tooltipTitle"], str | None]:
        """Returns a dict of the localized fields in the model."""
        if lang is None:
            return {
                "displayName": None,
                "tooltipDescription": None,
                "tooltipTitle": None,
            }
        return {
            "displayName": self.localized_displayName(lang),
            "tooltipDescription": self.localized_tooltipDescription(lang),
            "tooltipTitle": self.localized_tooltipTitle(lang),
        }

    def localized_displayName(self, lang: Lang) -> str | None:
        """Returns the localized display name for the given language."""
        lang_check(lang)
        return (
            self.displayName.get(lang, TRANSLATION_MISSING)
            if self.displayName
            else None
        )

    def localized_tooltipDescription(self, lang: Lang) -> str | None:
        """Returns the localized tooltip description for the given language."""
        lang_check(lang)
        return (
            self.tooltipDescription.get(lang, TRANSLATION_MISSING)
            if self.tooltipDescription
            else None
        )

    def localized_tooltipTitle(self, lang: Lang) -> str | None:
        """Returns the localized tooltip title for the given language."""
        lang_check(lang)
        return (
            self.tooltipTitle.get(lang, TRANSLATION_MISSING)
            if self.tooltipTitle
            else None
        )


@dataclass(slots=True, kw_only=True)
class DogmaEffects_ModifierInfo:
    """Nested model for the dogmaEffects.yaml SDE file."""

    domain: str
    effectID: int | None = None
    func: str
    groupID: int | None = None
    modifiedAttributeID: int | None = None
    modifyingAttributeID: int | None = None
    operation: int | None = None
    skillTypeID: int | None = None


@dataclass(slots=True, kw_only=True)
class DogmaEffects(LocalizableRecord):
    """Model for the dogmaEffects.yaml SDE file."""

    dogma_effects_id: int | None = None
    disallowAutoRepeat: bool
    dischargeAttributeID: int | None = None
    durationAttributeID: int | None = None
    effectCategoryID: int
    electronicChance: bool
    guid: str | None = None
    isAssistance: bool
    isOffensive: bool
    isWarpSafe: bool
    name: str
    propulsionChance: bool
    published: bool
    rangeChance: bool
    distribution: int | None = None
    falloffAttributeID: int | None = None
    rangeAttributeID: int | None = None
    trackingSpeedAttributeID: int | None = None
    description: LocalizedString | None = None
    displayName: LocalizedString | None = None
    iconID: int | None = None
    modifierInfo: list[DogmaEffects_ModifierInfo] | None = None
    npcUsageChanceAttributeID: int | None = None
    npcActivationChanceAttributeID: int | None = None
    fittingUsageChanceAttributeID: int | None = None
    resistanceAttributeID: int | None = None

    def localized_fields(
        self, lang: Lang | None
    ) -> dict[Literal["description", "displayName"], str | None]:
        """Returns a dict of the localized fields in the model."""
        if lang is None:
            return {"description": None, "displayName": None}
        return {
            "description": self.localized_description(lang),
            "displayName": self.localized_displayName(lang),
        }

    def localized_description(self, lang: Lang) -> str | None:
        """Returns the localized description for the given language."""
        lang_check(lang)
        return (
            self.description.get(lang, TRANSLATION_MISSING)
            if self.description
            else None
        )

    def localized_displayName(self, lang: Lang) -> str | None:
        """Returns the localized display name for the given language."""
        lang_check(lang)
        return (
            self.displayName.get(lang, TRANSLATION_MISSING)
            if self.displayName
            else None
        )


@dataclass(slots=True, kw_only=True)
class DogmaUnits(LocalizableRecord):
    """Model for the dogmaUnits.yaml SDE file."""

    dogma_units_id: int | None = None
    description: LocalizedString | None = None
    displayName: LocalizedString | None = None
    name: str

    def localized_fields(
        self, lang: Lang | None
    ) -> dict[Literal["description", "displayName"], str | None]:
        """Returns a dict of the localized fields in the model."""
        if lang is None:
            return {"description": None, "displayName": None}
        return {
            "displayName": self.localized_displayName(lang),
            "description": self.localized_description(lang),
        }

    def localized_displayName(self, lang: Lang) -> str | None:
        """Returns the localized display name for the given language."""
        lang_check(lang)
        return (
            self.displayName.get(lang, TRANSLATION_MISSING)
            if self.displayName
            else None
        )

    def localized_description(self, lang: Lang) -> str | None:
        """Returns the localized description for the given language."""
        lang_check(lang)
        return (
            self.description.get(lang, TRANSLATION_MISSING)
            if self.description
            else None
        )


@dataclass(slots=True, kw_only=True)
class DynamicItemAttributes_AttributeID:
    """Nested model for the dynamicItemAttributes.yaml SDE file."""

    highIsGood: bool | None = None
    max: float
    min: float


@dataclass(slots=True, kw_only=True)
class DynamicItemAttributes_InputOutputMapping:
    """Nested model for the dynamicItemAttributes.yaml SDE file."""

    applicableTypes: list[int]
    resultingType: int


@dataclass(slots=True, kw_only=True)
class DynamicItemAttributes:
    """Model for the dynamicItemAttributes.yaml SDE file."""

    dynamic_item_attributes_id: int | None = None
    attributeIDs: dict[int, DynamicItemAttributes_AttributeID]
    inputOutputMapping: list[DynamicItemAttributes_InputOutputMapping]


@dataclass(slots=True, kw_only=True)
class Factions(LocalizableRecord):
    """Model for the factions.yaml SDE file."""

    factions_id: int | None = None
    corporationID: int | None = None
    description: LocalizedString
    flatLogo: str | None = None
    flatLogoWithName: str | None = None
    iconID: int
    memberRaces: list[int]
    militiaCorporationID: int | None = None
    name: LocalizedString
    shortDescription: LocalizedString | None = None
    sizeFactor: float
    solarSystemID: int
    uniqueName: bool

    def localized_fields(
        self, lang: Lang | None
    ) -> dict[Literal["description", "name", "shortDescription"], str | None]:
        """Returns a dict of the localized fields in the model."""
        if lang is None:
            return {"description": None, "name": None, "shortDescription": None}
        return {
            "description": self.localized_description(lang),
            "name": self.localized_name(lang),
            "shortDescription": self.localized_shortDescription(lang),
        }

    def localized_description(self, lang: Lang) -> str:
        """Returns the localized description for the given language."""
        lang_check(lang)
        return self.description.get(lang, TRANSLATION_MISSING)

    def localized_name(self, lang: Lang) -> str:
        """Returns the localized name for the given language."""
        lang_check(lang)
        return self.name.get(lang, TRANSLATION_MISSING)

    def localized_shortDescription(self, lang: Lang) -> str | None:
        """Returns the localized short description for the given language."""
        lang_check(lang)
        return (
            self.shortDescription.get(lang, TRANSLATION_MISSING)
            if self.shortDescription
            else None
        )


type FreelanceJobSchemas = dict[str, Any]
"""Model for the freelanceJobSchemas.yaml SDE file."""


@dataclass(slots=True, kw_only=True)
class Graphics:
    """Model for the graphics.yaml SDE file."""

    graphics_id: int | None = None
    graphicFile: str | None = None
    iconFolder: str | None = None
    sofFactionName: str | None = None
    sofHullName: str | None = None
    sofRaceName: str | None = None
    sofMaterialSetID: int | None = None
    sofLayout: list[str] | None = None


@dataclass(slots=True, kw_only=True)
class Groups(LocalizableRecord):
    """Model for the groups.yaml SDE file."""

    groups_id: int | None = None
    anchorable: bool
    anchored: bool
    categoryID: int
    fittableNonSingleton: bool
    name: LocalizedString
    published: bool
    useBasePrice: bool
    iconID: int | None = None

    def localized_fields(self, lang: Lang | None) -> dict[Literal["name"], str | None]:
        """Returns a dict of the localized fields in the model."""
        if lang is None:
            return {"name": None}
        return {"name": self.localized_name(lang)}

    def localized_name(self, lang: Lang) -> str:
        """Returns the localized name for the given language."""
        lang_check(lang)
        return self.name.get(lang, TRANSLATION_MISSING)


@dataclass(slots=True, kw_only=True)
class Icons:
    """Model for the icons.yaml SDE file."""

    icons_id: int | None = None
    iconFile: str


@dataclass(slots=True, kw_only=True)
class Landmarks(LocalizableRecord):
    """Model for the landmarks.yaml SDE file."""

    landmarks_id: int | None = None
    description: LocalizedString
    name: LocalizedString
    position: Position
    iconID: int | None = None
    locationID: int | None = None

    def localized_fields(
        self, lang: Lang | None
    ) -> dict[Literal["description", "name"], str | None]:
        """Returns a dict of the localized fields in the model."""
        if lang is None:
            return {"description": None, "name": None}
        return {
            "description": self.localized_description(lang),
            "name": self.localized_name(lang),
        }

    def localized_description(self, lang: Lang) -> str:
        """Returns the localized description for the given language."""
        lang_check(lang)
        return self.description.get(lang, TRANSLATION_MISSING)

    def localized_name(self, lang: Lang) -> str:
        """Returns the localized name for the given language."""
        lang_check(lang)
        return self.name.get(lang, TRANSLATION_MISSING)


@dataclass(slots=True, kw_only=True)
class MapAsteroidBelts_Statistics:
    """Nested model for the mapAsteroidBelts.yaml SDE file."""

    density: float
    eccentricity: float
    escapeVelocity: float
    locked: bool
    massDust: float
    massGas: float | None = None
    orbitPeriod: float
    orbitRadius: float
    rotationRate: float
    spectralClass: str
    surfaceGravity: float
    temperature: float


@dataclass(slots=True, kw_only=True)
class MapAsteroidBelts(LocalizableRecord):
    """Model for the mapAsteroidBelts.yaml SDE file."""

    map_asteroid_belts_id: int | None = None
    celestialIndex: int
    orbitID: int
    orbitIndex: int
    position: Position
    radius: float | None = None
    solarSystemID: int
    statistics: MapAsteroidBelts_Statistics | None = None
    typeID: int
    uniqueName: LocalizedString | None = None

    def localized_fields(
        self, lang: Lang | None
    ) -> dict[Literal["uniqueName"], str | None]:
        """Returns a dict of the localized fields in the model."""
        if lang is None:
            return {"uniqueName": None}
        return {"uniqueName": self.localized_uniqueName(lang)}

    def localized_uniqueName(self, lang: Lang) -> str | None:
        """Returns the localized unique name for the given language."""
        lang_check(lang)
        return (
            self.uniqueName.get(lang, TRANSLATION_MISSING) if self.uniqueName else None
        )


@dataclass(slots=True, kw_only=True)
class MapConstellations(LocalizableRecord):
    """Model for the mapConstellations.yaml SDE file."""

    map_constellations_id: int | None = None
    factionID: int | None = None
    name: LocalizedString
    position: Position
    regionID: int
    solarSystemIDs: list[int]
    wormholeClassID: int | None = None

    def localized_fields(self, lang: Lang | None) -> dict[Literal["name"], str | None]:
        """Returns a dict of the localized fields in the model."""
        if lang is None:
            return {"name": None}
        return {"name": self.localized_name(lang)}

    def localized_name(self, lang: Lang) -> str:
        """Returns the localized name for the given language."""
        lang_check(lang)
        return self.name.get(lang, TRANSLATION_MISSING)


@dataclass(slots=True, kw_only=True)
class MapMoons_Attributes:
    """Nested model for the mapMoons.yaml SDE file."""

    heightMap1: int
    heightMap2: int
    shaderPreset: int


@dataclass(slots=True, kw_only=True)
class MapMoons_Statistics:
    """Nested model for the mapMoons.yaml SDE file."""

    density: float
    eccentricity: float
    escapeVelocity: float
    locked: bool
    massDust: float
    massGas: float | None = None
    orbitPeriod: float
    orbitRadius: float
    pressure: float
    rotationRate: float
    spectralClass: str
    surfaceGravity: float
    temperature: float


@dataclass(slots=True, kw_only=True)
class MapMoons(LocalizableRecord):
    """Model for the mapMoons.yaml SDE file."""

    map_moons_id: int | None = None
    attributes: MapMoons_Attributes
    celestialIndex: int
    orbitID: int
    orbitIndex: int
    position: Position
    radius: float
    solarSystemID: int
    statistics: MapMoons_Statistics | None = None
    typeID: int
    npcStationIDs: list[int] | None = None
    uniqueName: LocalizedString | None = None

    def localized_fields(
        self, lang: Lang | None
    ) -> dict[Literal["uniqueName"], str | None]:
        """Returns a dict of the localized fields in the model."""
        if lang is None:
            return {"uniqueName": None}
        return {"uniqueName": self.localized_uniqueName(lang)}

    def localized_uniqueName(self, lang: Lang) -> str | None:
        """Returns the localized unique name for the given language."""
        lang_check(lang)
        return (
            self.uniqueName.get(lang, TRANSLATION_MISSING) if self.uniqueName else None
        )


@dataclass(slots=True, kw_only=True)
class MapPlanets_Attributes:
    """Nested model for the mapPlanets.yaml SDE file."""

    heightMap1: int
    heightMap2: int
    population: bool
    shaderPreset: int


@dataclass(slots=True, kw_only=True)
class MapPlanets_Statistics:
    """Nested model for the mapPlanets.yaml SDE file."""

    density: float
    eccentricity: float
    escapeVelocity: float
    locked: bool
    massDust: float
    massGas: float | None = None
    orbitPeriod: float | None = None
    orbitRadius: float | None = None
    pressure: float
    rotationRate: float
    spectralClass: str
    surfaceGravity: float | None = None
    temperature: float


@dataclass(slots=True, kw_only=True)
class MapPlanets(LocalizableRecord):
    """Model for the mapPlanets.yaml SDE file."""

    map_planets_id: int | None = None
    asteroidBeltIDs: list[int] | None = None
    attributes: MapPlanets_Attributes
    celestialIndex: int
    moonIDs: list[int] | None = None
    orbitID: int
    position: Position
    radius: int
    solarSystemID: int
    statistics: MapPlanets_Statistics | None = None
    typeID: int
    npcStationIDs: list[int] | None = None
    uniqueName: LocalizedString | None = None

    def localized_fields(
        self, lang: Lang | None
    ) -> dict[Literal["uniqueName"], str | None]:
        """Returns a dict of the localized fields in the model."""
        if lang is None:
            return {"uniqueName": None}
        return {"uniqueName": self.localized_uniqueName(lang)}

    def localized_uniqueName(self, lang: Lang) -> str | None:
        """Returns the localized unique name for the given language."""
        lang_check(lang)
        return (
            self.uniqueName.get(lang, TRANSLATION_MISSING) if self.uniqueName else None
        )


@dataclass(slots=True, kw_only=True)
class MapRegions(LocalizableRecord):
    """Model for the mapRegions.yaml SDE file."""

    map_regions_id: int | None = None
    constellationIDs: list[int]
    description: LocalizedString | None = None
    factionID: int | None = None
    name: LocalizedString
    nebulaID: int
    position: Position
    wormholeClassID: int | None = None

    def localized_fields(
        self, lang: Lang | None
    ) -> dict[Literal["description", "name"], str | None]:
        """Returns a dict of the localized fields in the model."""
        if lang is None:
            return {"description": None, "name": None}

        return {
            "description": self.localized_description(lang),
            "name": self.localized_name(lang),
        }

    def localized_name(self, lang: Lang) -> str:
        """Returns the localized name for the given language."""
        lang_check(lang)
        return self.name.get(lang, TRANSLATION_MISSING)

    def localized_description(self, lang: Lang) -> str | None:
        """Returns the localized description for the given language."""
        lang_check(lang)
        return (
            self.description.get(lang, TRANSLATION_MISSING)
            if self.description
            else None
        )


@dataclass(slots=True, kw_only=True)
class MapSecondarySuns:
    """Model for the mapSecondarySuns.yaml SDE file."""

    map_secondary_suns_id: int | None = None
    effectBeaconTypeID: int
    position: Position
    solarSystemID: int
    typeID: int


@dataclass(slots=True, kw_only=True)
class MapSolarSystems(LocalizableRecord):
    """Model for the mapSolarSystems.yaml SDE file."""

    map_solar_systems_id: int | None = None
    border: bool | None = None
    constellationID: int
    corridor: bool | None = None
    disallowedAnchorCategories: list[int] | None = None
    disallowedAnchorGroups: list[int] | None = None
    factionID: int | None = None
    fringe: bool | None = None
    hub: bool | None = None
    international: bool | None = None
    luminosity: float | None = None
    name: LocalizedString
    planetIDs: list[int] | None = None
    position: Position
    position2D: Position2D | None = None
    radius: float
    regionID: int
    regional: bool | None = None
    securityClass: str | None = None
    securityStatus: float
    starID: int | None = None
    stargateIDs: list[int] | None = None
    visualEffect: str | None = None
    wormholeClassID: int | None = None

    def localized_fields(self, lang: Lang | None) -> dict[Literal["name"], str | None]:
        """Returns a dict of the localized fields in the model."""
        if lang is None:
            return {"name": None}
        return {"name": self.localized_name(lang)}

    def localized_name(self, lang: Lang) -> str:
        """Returns the localized name for the given language."""
        lang_check(lang)
        return self.name.get(lang, TRANSLATION_MISSING)


@dataclass(slots=True, kw_only=True)
class MapStargates_Destination:
    """Nested model for the mapStargates.yaml SDE file."""

    solarSystemID: int
    stargateID: int


@dataclass(slots=True, kw_only=True)
class MapStargates:
    """Model for the mapStargates.yaml SDE file."""

    map_stargates_id: int | None = None
    destination: MapStargates_Destination
    position: Position
    solarSystemID: int
    typeID: int


@dataclass(slots=True, kw_only=True)
class MapStars_Statistics:
    """Nested model for the mapStars.yaml SDE file."""

    age: float
    life: float
    luminosity: float
    spectralClass: str
    temperature: float


@dataclass(slots=True, kw_only=True)
class MapStars:
    """Model for the mapStars.yaml SDE file."""

    map_stars_id: int | None = None
    radius: int
    solarSystemID: int
    statistics: MapStars_Statistics
    typeID: int


@dataclass(slots=True, kw_only=True)
class MarketGroups(LocalizableRecord):
    """Model for the marketGroups.yaml SDE file."""

    market_groups_id: int | None = None
    description: LocalizedString | None = None
    hasTypes: bool
    iconID: int | None = None
    name: LocalizedString
    parentGroupID: int | None = None

    def localized_fields(
        self, lang: Lang | None
    ) -> dict[Literal["name", "description"], str | None]:
        """Returns a dict of the localized fields in the model."""
        if lang is None:
            return {"description": None, "name": None}
        description = self.localized_description(lang)
        return {
            "description": description,
            "name": self.localized_name(lang),
        }

    def localized_name(self, lang: Lang) -> str:
        """Returns the localized name of the market group."""
        lang_check(lang)
        return self.name.get(lang, TRANSLATION_MISSING)

    def localized_description(self, lang: Lang) -> str | None:
        """Returns the localized description of the market group."""
        lang_check(lang)
        return (
            self.description.get(lang, TRANSLATION_MISSING)
            if self.description
            else None
        )


# FIXME: check to see if this is following the same pattern,
# where the _id field is captured in the records from the database.
type Masteries = dict[int, list[int]]
"""Model for the masteries.yaml SDE file."""


@dataclass(slots=True, kw_only=True)
class MetaGroups(LocalizableRecord):
    """Model for the metaGroups.yaml SDE file."""

    meta_groups_id: int | None = None
    color: Color | None = None
    name: LocalizedString
    iconID: int | None = None
    iconSuffix: str | None = None
    description: LocalizedString | None = None

    def localized_fields(
        self, lang: Lang | None
    ) -> dict[Literal["name", "description"], str | None]:
        """Returns a dict of the localized fields in the model."""
        if lang is None:
            return {"name": None, "description": None}
        return {
            "name": self.localized_name(lang),
            "description": self.localized_description(lang),
        }

    def localized_name(self, lang: Lang) -> str:
        """Returns the localized name of the meta group."""
        lang_check(lang)
        return self.name.get(lang, TRANSLATION_MISSING)

    def localized_description(self, lang: Lang) -> str | None:
        """Returns the localized description of the meta group."""
        lang_check(lang)
        return (
            self.description.get(lang, TRANSLATION_MISSING)
            if self.description
            else None
        )


@dataclass(slots=True, kw_only=True)
class MercenaryTacticalOperations(LocalizableRecord):
    """Model for the mercenaryTacticalOperations.yaml SDE file."""

    mercenary_tactical_operations_id: int | None = None
    anarchyImpact: int
    developmentImpact: int
    infomorphBonus: int
    dungeonID: int
    name: LocalizedString
    description: LocalizedString | None = None

    def localized_fields(
        self, lang: Lang | None
    ) -> dict[Literal["name", "description"], str | None]:
        """Returns a dict of the localized fields in the model."""
        if lang is None:
            return {"name": None, "description": None}
        return {
            "name": self.localized_name(lang),
            "description": self.localized_description(lang),
        }

    def localized_name(self, lang: Lang) -> str:
        """Returns the localized name of the mercenary tactical operation."""
        lang_check(lang)
        return self.name.get(lang, TRANSLATION_MISSING)

    def localized_description(self, lang: Lang) -> str | None:
        """Returns the localized description of the mercenary tactical operation."""
        lang_check(lang)
        return (
            self.description.get(lang, TRANSLATION_MISSING)
            if self.description
            else None
        )


@dataclass(slots=True, kw_only=True)
class NpcCharacters_Skill:
    """Nested model for the npcCharacters.yaml SDE file."""

    typeID: int


@dataclass(slots=True, kw_only=True)
class NpcCharacters_Agent:
    """Nested model for the npcCharacters.yaml SDE file."""

    agentTypeID: int
    divisionID: int
    isLocator: bool
    level: int


@dataclass(slots=True, kw_only=True)
class NpcCharacters(LocalizableRecord):
    """Model for the npcCharacters.yaml SDE file."""

    npc_characters_id: int | None = None
    bloodlineID: int
    ceo: bool
    corporationID: int
    gender: bool
    locationID: int | None = None
    name: LocalizedString
    raceID: int
    startDate: str | None = None
    uniqueName: bool
    skills: list[NpcCharacters_Skill] | None = None
    ancestryID: int | None = None
    careerID: int | None = None
    schoolID: int | None = None
    specialityID: int | None = None
    agent: NpcCharacters_Agent | None = None
    description: str | None = None

    def localized_fields(self, lang: Lang | None) -> dict[Literal["name"], str | None]:
        """Returns a dict of the localized fields in the model."""
        if lang is None:
            return {"name": None}
        return {"name": self.localized_name(lang)}

    def localized_name(self, lang: Lang) -> str:
        """Returns the localized name of the npc character."""
        lang_check(lang)
        return self.name.get(lang, TRANSLATION_MISSING)


@dataclass(slots=True, kw_only=True)
class NpcCorporationDivisions(LocalizableRecord):
    """Model for the npcCorporationDivisions.yaml SDE file."""

    npc_corporation_divisions_id: int | None = None
    displayName: str | None = None
    internalName: str
    leaderTypeName: LocalizedString
    name: LocalizedString
    description: LocalizedString | None = None

    def localized_fields(
        self, lang: Lang | None
    ) -> dict[Literal["name", "description", "leaderTypeName"], str | None]:
        """Returns a dict of the localized fields in the model."""
        if lang is None:
            return {"name": None, "description": None, "leaderTypeName": None}
        return {
            "name": self.localized_name(lang),
            "description": self.localized_description(lang),
            "leaderTypeName": self.localized_leaderTypeName(lang),
        }

    def localized_leaderTypeName(self, lang: Lang) -> str:
        """Returns the localized leader type name of the npc corporation division."""
        lang_check(lang)
        return self.leaderTypeName.get(lang, TRANSLATION_MISSING)

    def localized_name(self, lang: Lang) -> str:
        """Returns the localized name of the npc corporation division."""
        lang_check(lang)
        return self.name.get(lang, TRANSLATION_MISSING)

    def localized_description(self, lang: Lang) -> str | None:
        """Returns the localized description of the npc corporation division."""
        lang_check(lang)
        return (
            self.description.get(lang, TRANSLATION_MISSING)
            if self.description
            else None
        )


@dataclass(slots=True, kw_only=True)
class NpcCorporations_Divisions:
    """Nested model for the npcCorporations.yaml SDE file."""

    divisionNumber: int
    leaderID: int
    size: int


@dataclass(slots=True, kw_only=True)
class NpcCorporations(LocalizableRecord):
    """Model for the npcCorporations.yaml SDE file."""

    npc_corporations_id: int | None = None
    ceoID: int | None = None
    deleted: bool
    description: LocalizedString | None = None
    extent: str
    hasPlayerPersonnelManager: bool
    initialPrice: int
    memberLimit: int
    minSecurity: float
    minimumJoinStanding: int
    name: LocalizedString
    sendCharTerminationMessage: bool
    shares: int
    size: str
    stationID: int | None = None
    taxRate: float
    tickerName: str
    uniqueName: bool
    allowedMemberRaces: list[int] | None = None
    corporationTrades: dict[int, float] | None = None
    divisions: dict[int, NpcCorporations_Divisions] | None = None
    enemyID: int | None = None
    factionID: int | None = None
    friendID: int | None = None
    iconID: int | None = None
    investors: dict[int, int] | None = None
    lpOfferTables: list[int] | None = None
    mainActivityID: int | None = None
    raceID: int | None = None
    sizeFactor: float | None = None
    solarSystemID: int | None = None
    secondaryActivityID: int | None = None
    exchangeRates: dict[int, float] | None = None

    def localized_fields(
        self, lang: Lang | None
    ) -> dict[Literal["description", "name"], str | None]:
        """Returns a dict of the localized fields in the model."""
        if lang is None:
            return {"description": None, "name": None}
        return {
            "description": self.localized_description(lang),
            "name": self.localized_name(lang),
        }

    def localized_name(self, lang: Lang) -> str:
        """Returns the localized name of the npc corporation."""
        lang_check(lang)
        return self.name.get(lang, TRANSLATION_MISSING)

    def localized_description(self, lang: Lang) -> str | None:
        """Returns the localized description of the npc corporation."""
        lang_check(lang)
        return (
            self.description.get(lang, TRANSLATION_MISSING)
            if self.description
            else None
        )


@dataclass(slots=True, kw_only=True)
class NpcStations:
    """Model for the npcStations.yaml SDE file."""

    npc_stations_id: int | None = None
    celestialIndex: int | None = None
    operationID: int
    orbitID: int
    orbitIndex: int | None = None
    ownerID: int
    position: Position
    reprocessingEfficiency: float
    reprocessingHangarFlag: int
    reprocessingStationsTake: float
    solarSystemID: int
    typeID: int
    useOperationName: bool


@dataclass(slots=True, kw_only=True)
class PlanetResources_Reagent:
    """Nested model for the planetResources.yaml SDE file."""

    amount_per_cycle: int
    cycle_period: int
    secured_capacity: int
    type_id: int
    unsecured_capacity: int


@dataclass(slots=True, kw_only=True)
class PlanetResources:
    """Model for the planetResources.yaml SDE file."""

    planet_resources_id: int | None = None
    power: int | None = None
    workforce: int | None = None
    reagent: PlanetResources_Reagent | None = None


@dataclass(slots=True, kw_only=True)
class PlanetSchematics_Types:
    """Nested model for the planetSchematics.yaml SDE file."""

    isInput: bool
    quantity: int


@dataclass(slots=True, kw_only=True)
class PlanetSchematics(LocalizableRecord):
    """Model for the planetSchematics.yaml SDE file."""

    planet_schematics_id: int | None = None
    cycleTime: int
    name: LocalizedString
    pins: list[int]
    types: dict[int, PlanetSchematics_Types]

    def localized_fields(self, lang: Lang | None) -> dict[Literal["name"], str | None]:
        """Returns a dict of the localized fields in the model."""
        if lang is None:
            return {"name": None}
        return {"name": self.localized_name(lang)}

    def localized_name(self, lang: Lang) -> str:
        """Returns the localized name of the planet schematic."""
        lang_check(lang)
        return self.name.get(lang, TRANSLATION_MISSING)


@dataclass(slots=True, kw_only=True)
class Races(LocalizableRecord):
    """Model for the races.yaml SDE file."""

    races_id: int | None = None
    description: LocalizedString | None = None
    iconID: int | None = None
    name: LocalizedString
    shipTypeID: int | None = None
    skills: dict[int, int] | None = None

    def localized_fields(
        self, lang: Lang | None
    ) -> dict[Literal["name", "description"], str | None]:
        """Returns a dict of the localized fields in the model."""
        if lang is None:
            return {"name": None, "description": None}
        return {
            "name": self.localized_name(lang),
            "description": self.localized_description(lang),
        }

    def localized_name(self, lang: Lang) -> str:
        """Returns the localized name of the race."""
        lang_check(lang)
        return self.name.get(lang, TRANSLATION_MISSING)

    def localized_description(self, lang: Lang) -> str | None:
        """Returns the localized description of the race."""
        lang_check(lang)
        return (
            self.description.get(lang, TRANSLATION_MISSING)
            if self.description
            else None
        )


@dataclass(slots=True, kw_only=True)
class SdeInfo:
    """Model for the sdeInfo.yaml SDE file."""

    sde_info_id: str | None = None  # Included for completeness. is always 'sde'.
    buildNumber: int
    releaseDate: str


@dataclass(slots=True, kw_only=True)
class SkinLicenses:
    """Model for the skinLicenses.yaml SDE file."""

    skin_licenses_id: int | None = None
    duration: int
    licenseTypeID: int
    skinID: int
    isSingleUse: bool | None = None


@dataclass(slots=True, kw_only=True)
class SkinMaterials(LocalizableRecord):
    """Model for the skinMaterials.yaml SDE file."""

    skin_materials_id: int | None = None
    displayName: LocalizedString | None = None
    materialSetID: int

    def localized_fields(
        self, lang: Lang | None
    ) -> dict[Literal["displayName"], str | None]:
        """Returns a dict of the localized fields in the model."""
        if lang is None:
            return {"displayName": None}
        return {"displayName": self.localized_displayName(lang)}

    def localized_displayName(self, lang: Lang) -> str | None:
        """Returns the localized display name of the skin material."""
        lang_check(lang)
        return (
            self.displayName.get(lang, TRANSLATION_MISSING)
            if self.displayName
            else None
        )


@dataclass(slots=True, kw_only=True)
class Skins(LocalizableRecord):
    """Model for the skins.yaml SDE file."""

    skins_id: int | None = None
    allowCCPDevs: bool
    internalName: str
    skinMaterialID: int
    types: list[int]
    visibleSerenity: bool
    visibleTranquility: bool
    isStructureSkin: bool | None = None
    skinDescription: LocalizedString | None = None

    def localized_fields(
        self, lang: Lang | None
    ) -> dict[Literal["skinDescription"], str | None]:
        """Returns a dict of the localized fields in the model."""
        if lang is None:
            return {"skinDescription": None}

        return {"skinDescription": self.localized_skinDescription(lang)}

    def localized_skinDescription(self, lang: Lang) -> str | None:
        """Returns the localized skin description of the skin."""
        lang_check(lang)
        return (
            self.skinDescription.get(lang, TRANSLATION_MISSING)
            if self.skinDescription
            else None
        )


@dataclass(slots=True, kw_only=True)
class SovereigntyUpgrades_Fuel:
    """Nested model for the sovereigntyUpgrades.yaml SDE file."""

    hourly_upkeep: int
    startup_cost: int
    type_id: int


@dataclass(slots=True, kw_only=True)
class SovereigntyUpgrades:
    """Model for the sovereigntyUpgrades.yaml SDE file."""

    sovereignty_upgrades_id: int | None = None
    fuel: SovereigntyUpgrades_Fuel | None = None
    mutually_exclusive_group: str
    power_allocation: int | None = None
    power_production: int | None = None
    workforce_allocation: int | None = None
    workforce_production: int | None = None


@dataclass(slots=True, kw_only=True)
class StationOperations(LocalizableRecord):
    """Model for the stationOperations.yaml SDE file."""

    station_operations_id: int | None = None
    activityID: int
    border: float
    corridor: float
    description: LocalizedString | None = None
    fringe: float
    hub: float
    manufacturingFactor: float
    operationName: LocalizedString
    ratio: float
    researchFactor: float
    services: list[int]
    stationTypes: dict[int, int] | None = None

    def localized_fields(
        self, lang: Lang | None
    ) -> dict[Literal["description", "operationName"], str | None]:
        """Returns a dict of the localized fields in the model."""
        if lang is None:
            return {"description": None, "operationName": None}
        return {
            "description": self.localized_description(lang),
            "operationName": self.localized_operationName(lang),
        }

    def localized_operationName(self, lang: Lang) -> str:
        """Returns the localized operation name of the station operation."""
        lang_check(lang)
        return self.operationName.get(lang, TRANSLATION_MISSING)

    def localized_description(self, lang: Lang) -> str | None:
        """Returns the localized description of the station operation."""
        lang_check(lang)
        return (
            self.description.get(lang, TRANSLATION_MISSING)
            if self.description
            else None
        )


@dataclass(slots=True, kw_only=True)
class StationServices(LocalizableRecord):
    """Model for the stationServices.yaml SDE file."""

    station_services_id: int | None = None
    serviceName: LocalizedString
    description: LocalizedString | None = None

    def localized_fields(
        self, lang: Lang | None
    ) -> dict[Literal["serviceName", "description"], str | None]:
        """Returns a dict of the localized fields in the model."""
        if lang is None:
            return {"serviceName": None, "description": None}
        return {
            "serviceName": self.localized_serviceName(lang),
            "description": self.localized_description(lang),
        }

    def localized_serviceName(self, lang: Lang) -> str:
        """Returns the localized service name of the station service."""
        lang_check(lang)
        return self.serviceName.get(lang, TRANSLATION_MISSING)

    def localized_description(self, lang: Lang) -> str | None:
        """Returns the localized description of the station service."""
        lang_check(lang)
        return (
            self.description.get(lang, TRANSLATION_MISSING)
            if self.description
            else None
        )


@dataclass(slots=True, kw_only=True)
class TranslationLanguages:
    """Model for the translationLanguages.yaml SDE file."""

    translation_languages_id: str | None = None
    name: str


@dataclass(slots=True, kw_only=True)
class TypeBonus_RoleBonus(LocalizableRecord):
    """Nested model for the typeBonus.yaml SDE file."""

    bonus: int | float | None = None
    bonusText: LocalizedString
    importance: int
    unitID: int | None = None

    def localized_fields(
        self, lang: Lang | None
    ) -> dict[Literal["bonusText"], str | None]:
        """Returns a dict of the localized fields in the model."""
        if lang is None:
            return {"bonusText": None}
        return {"bonusText": self.localized_bonusText(lang)}

    def localized_bonusText(self, lang: Lang) -> str:
        """Returns the localized bonus text of the role bonus."""
        lang_check(lang)
        return self.bonusText.get(lang, TRANSLATION_MISSING)


@dataclass(slots=True, kw_only=True)
class TypeBonus_Types_Bonus(LocalizableRecord):
    """Nested model for the typeBonus.yaml SDE file."""

    bonus: int | float | None = None
    bonusText: LocalizedString
    importance: int
    unitID: int | None = None

    def localized_fields(
        self, lang: Lang | None
    ) -> dict[Literal["bonusText"], str | None]:
        """Returns a dict of the localized fields in the model."""
        if lang is None:
            return {"bonusText": None}
        return {"bonusText": self.localized_bonusText(lang)}

    def localized_bonusText(self, lang: Lang) -> str:
        """Returns the localized bonus text of the type bonus."""
        lang_check(lang)
        return self.bonusText.get(lang, TRANSLATION_MISSING)


@dataclass(slots=True, kw_only=True)
class TypeBonus_MiscBonus(LocalizableRecord):
    """Nested model for the typeBonus.yaml SDE file."""

    bonus: int | float | None = None
    bonusText: LocalizedString
    importance: int
    isPositive: bool | None = None
    unitID: int | None = None

    def localized_fields(
        self, lang: Lang | None
    ) -> dict[Literal["bonusText"], str | None]:
        """Returns a dict of the localized fields in the model."""
        if lang is None:
            return {"bonusText": None}
        return {"bonusText": self.localized_bonusText(lang)}

    def localized_bonusText(self, lang: Lang) -> str:
        """Returns the localized bonus text of the misc bonus."""
        lang_check(lang)
        return self.bonusText.get(lang, TRANSLATION_MISSING)


@dataclass(slots=True, kw_only=True)
class TypeBonus:
    """Model for the typeBonus.yaml SDE file."""

    type_bonus_id: int | None = None
    roleBonuses: list[TypeBonus_RoleBonus] | None = None
    types: dict[int, list[TypeBonus_Types_Bonus]] | None = None
    iconID: int | None = None
    miscBonuses: list[TypeBonus_MiscBonus] | None = None


@dataclass(slots=True, kw_only=True)
class TypeDogma_Attributes:
    """Nested model for the typeDogma.yaml SDE file."""

    attributeID: int
    value: float


@dataclass(slots=True, kw_only=True)
class TypeDogma_Effects:
    """Nested model for the typeDogma.yaml SDE file."""

    effectID: int
    isDefault: bool


@dataclass(slots=True, kw_only=True)
class TypeDogma:
    """Model for the typeDogma.yaml SDE file."""

    type_dogma_id: int | None = None
    dogmaAttributes: list[TypeDogma_Attributes]
    dogmaEffects: list[TypeDogma_Effects] | None = None


@dataclass(slots=True, kw_only=True)
class TypeMaterials_Material:
    """Nested model for the typeMaterials.yaml SDE file."""

    materialTypeID: int
    quantity: int


@dataclass(slots=True, kw_only=True)
class TypeMaterials_RandomizedMaterial:
    """Nested model for the typeMaterials.yaml SDE file."""

    materialTypeID: int
    quantityMax: int
    quantityMin: int


@dataclass(slots=True, kw_only=True)
class TypeMaterials:
    """Model for the typeMaterials.yaml SDE file."""

    type_materials_id: int | None = None
    materials: list[TypeMaterials_Material] | None = None
    randomizedMaterials: list[TypeMaterials_RandomizedMaterial] | None = None


@dataclass(slots=True, kw_only=True)
class EveTypes(LocalizableRecord):
    """Model for the types.yaml SDE file."""

    type_id: int | None = None
    groupID: int
    mass: float | None = None
    name: LocalizedString
    portionSize: int
    published: bool
    volume: float | None = None
    radius: float | None = None
    description: LocalizedString | None = None
    graphicID: int | None = None
    soundID: int | None = None
    iconID: int | None = None
    raceID: int | None = None
    basePrice: float | None = None
    marketGroupID: int | None = None
    capacity: float | None = None
    metaGroupID: int | None = None
    metaLevel: int | None = None
    variationParentTypeID: int | None = None
    factionID: int | None = None

    def localized_fields(
        self, lang: Lang | None
    ) -> dict[Literal["name", "description"], str | None]:
        """Returns a dict of the localized fields in the model."""
        if lang is None:
            return {"name": None, "description": None}
        return {
            "name": self.localized_name(lang),
            "description": self.localized_description(lang),
        }

    def localized_name(self, lang: Lang) -> str:
        """Returns the localized name of the Eve type."""
        lang_check(lang)
        return self.name.get(lang, TRANSLATION_MISSING)

    def localized_description(self, lang: Lang) -> str | None:
        """Returns the localized description of the Eve type."""
        lang_check(lang)
        return (
            self.description.get(lang, TRANSLATION_MISSING)
            if self.description
            else None
        )
