"""Pydantic model definitions for EVE SDE Datasets.

This module contains Pydantic model definitions for individual records in EVE SDE datasets.
These models are used to validate and parse the data from the SDE files,
ensuring that the data conforms to the expected structure and types.

Field names match those in the original SDE files, with the exception of `_key`, which
is renamed to `key` due to a conflict with pydantic.

Note that many fields in the SDE files are optional, and as such that field may be
missing in a given record. In the pydantic models, the field is defined as optional
and will be set to `None` if it is missing in the data.
"""

from collections.abc import Iterator
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from eve_static_data.helpers.jsonl_reader import read_jsonl_file
from eve_static_data.models.dataset_filenames import SdeDatasetFiles
from eve_static_data.transformers import ModelLoader

# ------------------------------------------------------------------------------
# Common Pydantic model definitions.
# ------------------------------------------------------------------------------


class LocalizedString(BaseModel):
    """Type definition for LocalizedString.

    Source info: SDE file: translationLanguages.jsonl
    """

    en: str = Field("NOT_TRANSLATED", description="English translation")
    de: str = Field("NOT_TRANSLATED", description="German translation")
    fr: str = Field("NOT_TRANSLATED", description="French translation")
    ja: str = Field("NOT_TRANSLATED", description="Japanese translation")
    zh: str = Field("NOT_TRANSLATED", description="Chinese translation")
    ru: str = Field("NOT_TRANSLATED", description="Russian translation")
    ko: str = Field("NOT_TRANSLATED", description="Korean translation")
    es: str = Field("NOT_TRANSLATED", description="Spanish translation")


class Materials(BaseModel):
    """Model used in multiple datasets for materials, e.g. in blueprints and typeMaterials."""

    typeID: int
    quantity: int


class Skills(BaseModel):
    """Model used in multiple datasets for skills, e.g. in blueprints and npcCharacters."""

    typeID: int
    level: int


class Color(BaseModel):
    """Model used in multiple datasets for color, e.g. in metaGroups."""

    b: float
    g: float
    r: float


class Position(BaseModel):
    """Model used in multiple datasets for position, e.g. in celestialObjects and npcCharacters."""

    x: float
    y: float
    z: float


class Position2D(BaseModel):
    """Model used in multiple datasets for 2D position, e.g. in mapSolarSystems."""

    x: float
    y: float


# ------------------------------------------------------------------------------
# File level Pydantic model definitions.
# ------------------------------------------------------------------------------


class SdeDatasetRecord(BaseModel):
    """Base model for all SDE datasets."""

    model_config = ConfigDict(serialize_by_alias=True)


class AgentsInSpace(SdeDatasetRecord):
    """Model for the agentsInSpace.jsonl SDE file."""

    key: int = Field(..., alias="_key")
    dungeonID: int
    solarSystemID: int
    spawnPointID: int
    typeID: int


class AgentTypes(SdeDatasetRecord):
    """Model for the agentTypes.jsonl SDE file."""

    key: int = Field(..., alias="_key")
    name: str


class Ancestries(SdeDatasetRecord):
    """Model for the ancestries.jsonl SDE file."""

    key: int = Field(..., alias="_key")
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


class Bloodlines(SdeDatasetRecord):
    """Model for the bloodlines.jsonl SDE file."""

    key: int = Field(..., alias="_key")
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


class Blueprints_Products(BaseModel):
    """Nested model for the blueprints.jsonl SDE file."""

    typeID: int
    quantity: int
    probability: float | None = None


class Blueprints_Activity(BaseModel):
    """Nested model for the blueprints.jsonl SDE file."""

    materials: list[Materials] | None = None
    skills: list[Skills] | None = None
    time: int
    products: list[Blueprints_Products] | None = None


class Blueprints_Activities(BaseModel):
    """Nested model for the blueprints.jsonl SDE file."""

    copying: Blueprints_Activity | None = None
    invention: Blueprints_Activity | None = None
    manufacturing: Blueprints_Activity | None = None
    reaction: Blueprints_Activity | None = None
    research_material: Blueprints_Activity | None = None
    research_time: Blueprints_Activity | None = None


class Blueprints(SdeDatasetRecord):
    """Model for the blueprints.jsonl SDE file."""

    key: int = Field(..., alias="_key")
    activities: Blueprints_Activities
    blueprintTypeID: int
    maxProductionLimit: int


class Categories(SdeDatasetRecord):
    """Model for the categories.jsonl SDE file."""

    key: int = Field(..., alias="_key")
    name: LocalizedString
    published: bool
    iconID: int | None = None


class Certificates_SkillType(BaseModel):
    """Nested model for the certificates.jsonl SDE file."""

    key: int = Field(..., alias="_key")
    basic: int
    standard: int
    improved: int
    advanced: int
    elite: int

    model_config = ConfigDict(serialize_by_alias=True)


class Certificates(SdeDatasetRecord):
    """Model for the certificates.jsonl SDE file."""

    key: int = Field(..., alias="_key")
    description: LocalizedString
    groupID: int
    name: LocalizedString
    recommendedFor: list[int] | None = None
    skillTypes: list[Certificates_SkillType]


class CharacterAttributes(SdeDatasetRecord):
    """Model for the characterAttributes.jsonl SDE file."""

    key: int = Field(..., alias="_key")
    description: str
    iconID: int
    name: LocalizedString
    notes: str
    shortDescription: str


class CloneGrades(SdeDatasetRecord):
    """Model for the cloneGrades.jsonl SDE file."""

    key: int = Field(..., alias="_key")
    name: str
    skills: list[Skills]


class CompressibleTypes(SdeDatasetRecord):
    """Model for the compressibleTypes.jsonl SDE file."""

    key: int = Field(..., alias="_key")
    compressedTypeID: int


class ContrabandTypes_Faction(SdeDatasetRecord):
    """Nested model for the contrabandTypes.jsonl SDE file."""

    key: int = Field(..., alias="_key")
    attackMinSec: float
    confiscateMinSec: float
    fineByValue: float
    standingLoss: float


class ContrabandTypes(SdeDatasetRecord):
    """Model for the contrabandTypes.jsonl SDE file."""

    key: int = Field(..., alias="_key")
    factions: list[ContrabandTypes_Faction]


class ControlTowerResources_Resource(BaseModel):
    """Nested model for the controlTowerResources.jsonl SDE file."""

    factionID: int | None = None
    minSecurityLevel: float | None = None
    purpose: int
    quantity: int
    resourceTypeID: int


class ControlTowerResources(SdeDatasetRecord):
    """Model for the controlTowerResources.jsonl SDE file."""

    key: int = Field(..., alias="_key")
    resources: list[ControlTowerResources_Resource]


class CorporationActivities(SdeDatasetRecord):
    """Model for the corporationActivities.jsonl SDE file."""

    key: int = Field(..., alias="_key")
    name: LocalizedString


class DebuffCollections_LocationGroupModifier(BaseModel):
    """Nested model for the debuffCollections.jsonl SDE file."""

    dogmaAttributeID: int
    groupID: int


class DebuffCollections_LocationModifier(BaseModel):
    """Nested model for the debuffCollections.jsonl SDE file."""

    dogmaAttributeID: int


class DebuffCollections_LocationRequiredSkillModifier(BaseModel):
    """Nested model for the debuffCollections.jsonl SDE file."""

    dogmaAttributeID: int
    skillID: int


class DebuffCollections_ItemModifier(BaseModel):
    """Nested model for the debuffCollections.jsonl SDE file."""

    dogmaAttributeID: int


class DebuffCollections(SdeDatasetRecord):
    """Model for the debuffCollections.jsonl SDE file."""

    key: int = Field(..., alias="_key")
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


class DogmaAttributeCategories(SdeDatasetRecord):
    """Model for the dogmaAttributeCategories.jsonl SDE file."""

    key: int = Field(..., alias="_key")
    description: str | None = None
    name: str


class DogmaAttributes(SdeDatasetRecord):
    """Model for the dogmaAttributes.jsonl SDE file."""

    key: int = Field(..., alias="_key")
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


class DogmaEffects_ModifierInfo(BaseModel):
    """Nested model for the dogmaEffects.jsonl SDE file."""

    domain: str
    effectID: int | None = None
    func: str
    groupID: int | None = None
    modifiedAttributeID: int | None = None
    modifyingAttributeID: int | None = None
    operation: int | None = None
    skillTypeID: int | None = None


class DogmaEffects(SdeDatasetRecord):
    """Model for the dogmaEffects.jsonl SDE file."""

    key: int = Field(..., alias="_key")
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


class DogmaUnits(SdeDatasetRecord):
    """Model for the dogmaUnits.jsonl SDE file."""

    key: int = Field(..., alias="_key")
    description: LocalizedString | None = None
    displayName: LocalizedString | None = None
    name: str


class DynamicItemAttributes_AttributeID(SdeDatasetRecord):
    """Nested model for the dynamicItemAttributes.jsonl SDE file."""

    key: int = Field(..., alias="_key")
    highIsGood: bool | None = None
    max: float
    min: float


class DynamicItemAttributes_InputOutputMapping(BaseModel):
    """Nested model for the dynamicItemAttributes.jsonl SDE file."""

    applicableTypes: list[int]
    resultingType: int


class DynamicItemAttributes(SdeDatasetRecord):
    """Model for the dynamicItemAttributes.jsonl SDE file."""

    key: int = Field(..., alias="_key")
    attributeIDs: list[DynamicItemAttributes_AttributeID]
    inputOutputMapping: list[DynamicItemAttributes_InputOutputMapping]


class Factions(SdeDatasetRecord):
    """Model for the factions.jsonl SDE file."""

    key: int = Field(..., alias="_key")
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


class FreelanceJobSchemas(SdeDatasetRecord):
    """Model for the freelanceJobSchemas.jsonl SDE file."""

    key: int = Field(..., alias="_key")
    value: list[dict[str, Any]] = Field(..., alias="_value")


class Graphics(SdeDatasetRecord):
    """Model for the graphics.jsonl SDE file."""

    key: int = Field(..., alias="_key")
    graphicFile: str | None = None
    iconFolder: str | None = None
    sofFactionName: str | None = None
    sofHullName: str | None = None
    sofRaceName: str | None = None
    sofMaterialSetID: int | None = None
    sofLayout: list[str] | None = None


class Groups(SdeDatasetRecord):
    """Model for the groups.jsonl SDE file."""

    key: int = Field(..., alias="_key")
    anchorable: bool
    anchored: bool
    categoryID: int
    fittableNonSingleton: bool
    name: LocalizedString
    published: bool
    useBasePrice: bool
    iconID: int | None = None


class Icons(SdeDatasetRecord):
    """Model for the icons.jsonl SDE file."""

    key: int = Field(..., alias="_key")
    iconFile: str


class Landmarks(SdeDatasetRecord):
    """Model for the landmarks.jsonl SDE file."""

    key: int = Field(..., alias="_key")
    description: LocalizedString
    name: LocalizedString
    position: Position
    iconID: int | None = None
    locationID: int | None = None


class MapAsteroidBelts_Statistics(BaseModel):
    """Nested model for the mapAsteroidBelts.jsonl SDE file."""

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


class MapAsteroidBelts(SdeDatasetRecord):
    """Model for the mapAsteroidBelts.jsonl SDE file."""

    key: int = Field(..., alias="_key")
    celestialIndex: int
    orbitID: int
    orbitIndex: int
    position: Position
    radius: float | None = None
    solarSystemID: int
    statistics: MapAsteroidBelts_Statistics | None = None
    typeID: int
    uniqueName: LocalizedString | None = None


class MapConstellations(SdeDatasetRecord):
    """Model for the mapConstellations.jsonl SDE file."""

    key: int = Field(..., alias="_key")
    factionID: int | None = None
    name: LocalizedString
    position: Position
    regionID: int
    solarSystemIDs: list[int]
    wormholeClassID: int | None = None


class MapMoons_Attributes(BaseModel):
    """Nested model for the mapMoons.jsonl SDE file."""

    heightMap1: int
    heightMap2: int
    shaderPreset: int


class MapMoons_Statistics(BaseModel):
    """Nested model for the mapMoons.jsonl SDE file."""

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


class MapMoons(SdeDatasetRecord):
    """Model for the mapMoons.jsonl SDE file."""

    key: int = Field(..., alias="_key")
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


class MapPlanets_Attributes(BaseModel):
    """Nested model for the mapPlanets.jsonl SDE file."""

    heightMap1: int
    heightMap2: int
    population: bool
    shaderPreset: int


class MapPlanets_Statistics(BaseModel):
    """Nested model for the mapPlanets.jsonl SDE file."""

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


class MapPlanets(SdeDatasetRecord):
    """Model for the mapPlanets.jsonl SDE file."""

    key: int = Field(..., alias="_key")
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


class MapRegions(SdeDatasetRecord):
    """Model for the mapRegions.jsonl SDE file."""

    key: int = Field(..., alias="_key")
    constellationIDs: list[int]
    description: LocalizedString | None = None
    factionID: int | None = None
    name: LocalizedString
    nebulaID: int
    position: Position
    wormholeClassID: int | None = None


class MapSecondarySuns(SdeDatasetRecord):
    """Model for the mapSecondarySuns.jsonl SDE file."""

    key: int = Field(..., alias="_key")
    effectBeaconTypeID: int
    position: Position
    solarSystemID: int
    typeID: int


class MapSolarSystems(SdeDatasetRecord):
    """Model for the mapSolarSystems.jsonl SDE file."""

    key: int = Field(..., alias="_key")
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


class MapStargates_Destination(BaseModel):
    """Nested model for the mapStargates.jsonl SDE file."""

    solarSystemID: int
    stargateID: int


class MapStargates(SdeDatasetRecord):
    """Model for the mapStargates.jsonl SDE file."""

    key: int = Field(..., alias="_key")
    destination: MapStargates_Destination
    position: Position
    solarSystemID: int
    typeID: int


class MapStars_Statistics(BaseModel):
    """Nested model for the mapStars.jsonl SDE file."""

    age: float
    life: float
    luminosity: float
    spectralClass: str
    temperature: float


class MapStars(SdeDatasetRecord):
    """Model for the mapStars.jsonl SDE file."""

    key: int = Field(..., alias="_key")
    radius: int
    solarSystemID: int
    statistics: MapStars_Statistics
    typeID: int


class MarketGroups(SdeDatasetRecord):
    """Model for the marketGroups.jsonl SDE file."""

    key: int = Field(..., alias="_key")
    description: LocalizedString | None = None
    hasTypes: bool
    iconID: int | None = None
    name: LocalizedString
    parentGroupID: int | None = None


class Masteries_Value(SdeDatasetRecord):
    """Nested model for the masteries.jsonl SDE file."""

    key: int = Field(..., alias="_key")
    value: list[int] = Field(..., alias="_value")


class Masteries(SdeDatasetRecord):
    """Model for the masteries.jsonl SDE file."""

    key: int = Field(..., alias="_key")
    value: list[Masteries_Value] = Field(..., alias="_value")


class MetaGroups(SdeDatasetRecord):
    """Model for the metaGroups.jsonl SDE file."""

    key: int = Field(..., alias="_key")
    color: Color | None = None
    name: LocalizedString
    iconID: int | None = None
    iconSuffix: str | None = None
    description: LocalizedString | None = None


class MercenaryTacticalOperations(SdeDatasetRecord):
    """Model for the mercenaryTacticalOperations.jsonl SDE file."""

    key: int = Field(..., alias="_key")
    anarchy_impact: int
    development_impact: int
    infomorph_bonus: int
    name: LocalizedString
    description: LocalizedString | None = None


class NpcCharacters_Skill(BaseModel):
    """Nested model for the npcCharacters.jsonl SDE file."""

    typeID: int


class NpcCharacters_Agent(BaseModel):
    """Nested model for the npcCharacters.jsonl SDE file."""

    agentTypeID: int
    divisionID: int
    isLocator: bool
    level: int


class NpcCharacters(SdeDatasetRecord):
    """Model for the npcCharacters.jsonl SDE file."""

    key: int = Field(..., alias="_key")
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


class NpcCorporationDivisions(SdeDatasetRecord):
    """Model for the npcCorporationDivisions.jsonl SDE file."""

    key: int = Field(..., alias="_key")
    displayName: str | None = None
    internalName: str
    leaderTypeName: LocalizedString
    name: LocalizedString
    description: LocalizedString | None = None


class NpcCorporations_Trade(SdeDatasetRecord):
    """Nested model for the npcCorporations.jsonl SDE file."""

    key: int = Field(..., alias="_key")
    value: float = Field(..., alias="_value")


class NpcCorporations_Divisions(SdeDatasetRecord):
    """Nested model for the npcCorporations.jsonl SDE file."""

    key: int = Field(..., alias="_key")
    divisionNumber: int
    leaderID: int
    size: int


class NpcCorporations_Investors(SdeDatasetRecord):
    """Nested model for the npcCorporations.jsonl SDE file."""

    key: int = Field(..., alias="_key")
    value: int = Field(..., alias="_value")


class NpcCorporations_ExchangeRates(SdeDatasetRecord):
    """Nested model for the npcCorporations.jsonl SDE file."""

    key: int = Field(..., alias="_key")
    value: float = Field(..., alias="_value")


class NpcCorporations(SdeDatasetRecord):
    """Model for the npcCorporations.jsonl SDE file."""

    key: int = Field(..., alias="_key")
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
    corporationTrades: list[NpcCorporations_Trade] | None = None
    divisions: list[NpcCorporations_Divisions] | None = None
    enemyID: int | None = None
    factionID: int | None = None
    friendID: int | None = None
    iconID: int | None = None
    investors: list[NpcCorporations_Investors] | None = None
    lpOfferTables: list[int] | None = None
    mainActivityID: int | None = None
    raceID: int | None = None
    sizeFactor: float | None = None
    solarSystemID: int | None = None
    secondaryActivityID: int | None = None
    exchangeRates: list[NpcCorporations_ExchangeRates] | None = None


class NpcStations(SdeDatasetRecord):
    """Model for the npcStations.jsonl SDE file."""

    key: int = Field(..., alias="_key")
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


class PlanetResources_Reagent(BaseModel):
    """Nested model for the planetResources.jsonl SDE file."""

    amount_per_cycle: int
    cycle_period: int
    secured_capacity: int
    type_id: int
    unsecured_capacity: int


class PlanetResources(SdeDatasetRecord):
    """Model for the planetResources.jsonl SDE file."""

    key: int = Field(..., alias="_key")
    power: int | None = None
    workforce: int | None = None
    reagent: PlanetResources_Reagent | None = None


class PlanetSchematics_Types(BaseModel):
    """Nested model for the planetSchematics.jsonl SDE file."""

    key: int = Field(..., alias="_key")
    isInput: bool
    quantity: int

    model_config = ConfigDict(serialize_by_alias=True)


class PlanetSchematics(SdeDatasetRecord):
    """Model for the planetSchematics.jsonl SDE file."""

    key: int = Field(..., alias="_key")
    cycleTime: int
    name: LocalizedString
    pins: list[int]
    types: list[PlanetSchematics_Types]


class Races_Skill(BaseModel):
    """Nested model for the races.jsonl SDE file."""

    key: int = Field(..., alias="_key")
    value: int = Field(..., alias="_value")

    model_config = ConfigDict(serialize_by_alias=True)


class Races(SdeDatasetRecord):
    """Model for the races.jsonl SDE file."""

    key: int = Field(..., alias="_key")
    description: LocalizedString | None = None
    iconID: int | None = None
    name: LocalizedString
    shipTypeID: int | None = None
    skills: list[Races_Skill] | None = None


class SdeInfo(SdeDatasetRecord):
    """Model for the sdeInfo.jsonl SDE file."""

    key: str = Field(..., alias="_key")
    buildNumber: int
    releaseDate: str


class SkinLicenses(SdeDatasetRecord):
    """Model for the skinLicenses.jsonl SDE file."""

    key: int = Field(..., alias="_key")
    duration: int
    licenseTypeID: int
    skinID: int
    isSingleUse: bool | None = None


class SkinMaterials(SdeDatasetRecord):
    """Model for the skinMaterials.jsonl SDE file."""

    key: int = Field(..., alias="_key")
    displayName: LocalizedString | None = None
    materialSetID: int


class Skins(SdeDatasetRecord):
    """Model for the skins.jsonl SDE file."""

    key: int = Field(..., alias="_key")
    allowCCPDevs: bool
    internalName: str
    skinMaterialID: int
    types: list[int]
    visibleSerenity: bool
    visibleTranquility: bool
    isStructureSkin: bool | None = None
    skinDescription: LocalizedString | None = None


class SovereigntyUpgrades_Fuel(BaseModel):
    """Nested model for the sovereigntyUpgrades.jsonl SDE file."""

    hourly_upkeep: int
    startup_cost: int
    type_id: int


class SovereigntyUpgrades(SdeDatasetRecord):
    """Model for the sovereigntyUpgrades.jsonl SDE file."""

    key: int = Field(..., alias="_key")
    fuel: SovereigntyUpgrades_Fuel | None = None
    mutually_exclusive_group: str
    power_allocation: int | None = None
    power_production: int | None = None
    workforce_allocation: int | None = None
    workforce_production: int | None = None


class StationOperations_StationType(SdeDatasetRecord):
    """Nested model for the stationOperations.jsonl SDE file."""

    key: int = Field(..., alias="_key")
    value: int = Field(..., alias="_value")

    model_config = ConfigDict(serialize_by_alias=True)


class StationOperations(SdeDatasetRecord):
    """Model for the stationOperations.jsonl SDE file."""

    key: int = Field(..., alias="_key")
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
    stationTypes: list[StationOperations_StationType] | None = None


class StationServices(SdeDatasetRecord):
    """Model for the stationServices.jsonl SDE file."""

    key: int = Field(..., alias="_key")
    serviceName: LocalizedString
    description: LocalizedString | None = None


class TranslationLanguages(SdeDatasetRecord):
    """Model for the translationLanguages.jsonl SDE file."""

    key: str = Field(..., alias="_key")
    name: str


class TypeBonus_RoleBonus(BaseModel):
    """Nested model for the typeBonus.jsonl SDE file."""

    bonus: int | float | None = None
    bonusText: LocalizedString
    importance: int
    unitID: int | None = None


class TypeBonus_Types_Bonus(BaseModel):
    """Nested model for the typeBonus.jsonl SDE file."""

    bonus: int | float | None = None
    bonusText: LocalizedString
    importance: int
    unitID: int | None = None


class TypeBonus_Types(BaseModel):
    """Nested model for the typeBonus.jsonl SDE file."""

    key: int = Field(..., alias="_key")
    value: list[TypeBonus_Types_Bonus] = Field(..., alias="_value")

    model_config = ConfigDict(serialize_by_alias=True)


class TypeBonus_MiscBonus(BaseModel):
    """Nested model for the typeBonus.jsonl SDE file."""

    bonus: int | float | None = None
    bonusText: LocalizedString
    importance: int
    isPositive: bool | None = None
    unitID: int | None = None


class TypeBonus(SdeDatasetRecord):
    """Model for the typeBonus.jsonl SDE file."""

    key: int = Field(..., alias="_key")
    roleBonuses: list[TypeBonus_RoleBonus] | None = None
    types: list[TypeBonus_Types] | None = None
    iconID: int | None = None
    miscBonuses: list[TypeBonus_MiscBonus] | None = None


class TypeDogma_Attributes(BaseModel):
    """Nested model for the typeDogma.jsonl SDE file."""

    attributeID: int
    value: float


class TypeDogma_Effects(BaseModel):
    """Nested model for the typeDogma.jsonl SDE file."""

    effectID: int
    isDefault: bool


class TypeDogma(SdeDatasetRecord):
    """Model for the typeDogma.jsonl SDE file."""

    key: int = Field(..., alias="_key")
    dogmaAttributes: list[TypeDogma_Attributes]
    dogmaEffects: list[TypeDogma_Effects] | None = None


class TypeMaterials_Material(BaseModel):
    """Nested model for the typeMaterials.jsonl SDE file."""

    materialTypeID: int
    quantity: int


class TypeMaterials_RandomizedMaterial(BaseModel):
    """Nested model for the typeMaterials.jsonl SDE file."""

    materialTypeID: int
    quantityMax: int
    quantityMin: int


class TypeMaterials(SdeDatasetRecord):
    """Model for the typeMaterials.jsonl SDE file."""

    key: int = Field(..., alias="_key")
    materials: list[TypeMaterials_Material] | None = None
    randomizedMaterials: list[TypeMaterials_RandomizedMaterial] | None = None


class EveTypes(SdeDatasetRecord):
    """Model for the types.jsonl SDE file."""

    key: int = Field(..., alias="_key")
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
    variationParentTypeID: int | None = None
    factionID: int | None = None


LOOKUP: dict[SdeDatasetFiles, type[SdeDatasetRecord]] = {
    SdeDatasetFiles.AGENTS_IN_SPACE: AgentsInSpace,
    SdeDatasetFiles.AGENT_TYPES: AgentTypes,
    SdeDatasetFiles.ANCESTRIES: Ancestries,
    SdeDatasetFiles.BLOODLINES: Bloodlines,
    SdeDatasetFiles.BLUEPRINTS: Blueprints,
    SdeDatasetFiles.CATEGORIES: Categories,
    SdeDatasetFiles.CERTIFICATES: Certificates,
    SdeDatasetFiles.CHARACTER_ATTRIBUTES: CharacterAttributes,
    SdeDatasetFiles.CLONE_GRADES: CloneGrades,
    SdeDatasetFiles.COMPRESSIBLE_TYPES: CompressibleTypes,
    SdeDatasetFiles.CONTRABAND_TYPES: ContrabandTypes,
    SdeDatasetFiles.CONTROL_TOWER_RESOURCES: ControlTowerResources,
    SdeDatasetFiles.CORPORATION_ACTIVITIES: CorporationActivities,
    SdeDatasetFiles.DBUFF_COLLECTIONS: DebuffCollections,
    SdeDatasetFiles.DOGMA_ATTRIBUTE_CATEGORIES: DogmaAttributeCategories,
    SdeDatasetFiles.DOGMA_ATTRIBUTES: DogmaAttributes,
    SdeDatasetFiles.DOGMA_EFFECTS: DogmaEffects,
    SdeDatasetFiles.DOGMA_UNITS: DogmaUnits,
    SdeDatasetFiles.DYNAMIC_ITEM_ATTRIBUTES: DynamicItemAttributes,
    SdeDatasetFiles.FACTIONS: Factions,
    SdeDatasetFiles.FREELANCE_JOB_SCHEMAS: FreelanceJobSchemas,
    SdeDatasetFiles.GRAPHICS: Graphics,
    SdeDatasetFiles.GROUPS: Groups,
    SdeDatasetFiles.ICONS: Icons,
    SdeDatasetFiles.LANDMARKS: Landmarks,
    SdeDatasetFiles.MAP_ASTEROID_BELTS: MapAsteroidBelts,
    SdeDatasetFiles.MAP_CONSTELLATIONS: MapConstellations,
    SdeDatasetFiles.MAP_MOONS: MapMoons,
    SdeDatasetFiles.MAP_PLANETS: MapPlanets,
    SdeDatasetFiles.MAP_REGIONS: MapRegions,
    SdeDatasetFiles.MAP_SECONDARY_SUNS: MapSecondarySuns,
    SdeDatasetFiles.MAP_SOLAR_SYSTEMS: MapSolarSystems,
    SdeDatasetFiles.MAP_STARGATES: MapStargates,
    SdeDatasetFiles.MAP_STARS: MapStars,
    SdeDatasetFiles.MARKET_GROUPS: MarketGroups,
    SdeDatasetFiles.MASTERIES: Masteries,
    SdeDatasetFiles.META_GROUPS: MetaGroups,
    SdeDatasetFiles.MERCENARY_TACTICAL_OPERATIONS: MercenaryTacticalOperations,
    SdeDatasetFiles.NPC_CHARACTERS: NpcCharacters,
    SdeDatasetFiles.NPC_CORPORATION_DIVISIONS: NpcCorporationDivisions,
    SdeDatasetFiles.NPC_CORPORATIONS: NpcCorporations,
    SdeDatasetFiles.NPC_STATIONS: NpcStations,
    SdeDatasetFiles.PLANET_RESOURCES: PlanetResources,
    SdeDatasetFiles.PLANET_SCHEMATICS: PlanetSchematics,
    SdeDatasetFiles.RACES: Races,
    SdeDatasetFiles.SDE_INFO: SdeInfo,
    SdeDatasetFiles.SKIN_LICENSES: SkinLicenses,
    SdeDatasetFiles.SKIN_MATERIALS: SkinMaterials,
    SdeDatasetFiles.SKINS: Skins,
    SdeDatasetFiles.SOVEREIGNTY_UPGRADES: SovereigntyUpgrades,
    SdeDatasetFiles.STATION_OPERATIONS: StationOperations,
    SdeDatasetFiles.STATION_SERVICES: StationServices,
    SdeDatasetFiles.TRANSLATION_LANGUAGES: TranslationLanguages,
    SdeDatasetFiles.TYPE_BONUS: TypeBonus,
    SdeDatasetFiles.TYPE_DOGMA: TypeDogma,
    SdeDatasetFiles.TYPE_MATERIALS: TypeMaterials,
    SdeDatasetFiles.TYPES: EveTypes,
}
REVERSE: dict[str, SdeDatasetFiles] = {
    model.__name__: dataset_file for dataset_file, model in LOOKUP.items()
}


def get_model_for_dataset_file(dataset_file: SdeDatasetFiles) -> type[SdeDatasetRecord]:
    """Get the pydantic model class for a given SDE dataset file.

    Args:
        dataset_file: The SdeDatasetFiles enum member representing the dataset file.

    Returns:
        The pydantic model class associated with the given dataset file.

    Raises:
        ValueError: If no model is registered for the given dataset file.
    """
    if dataset_file in LOOKUP:
        return LOOKUP[dataset_file]
    raise ValueError(f"No model found for dataset file: {dataset_file}")


def get_transformer[T: SdeDatasetRecord](
    model: type[T], only_published: bool, skip_validation_failures: bool
) -> ModelLoader[T]:
    """Get the transformer for a given model type.

    Args:
        model: The pydantic model class to build a transformer for.
        only_published: Whether to only include published records.
        skip_validation_failures: Whether to skip records that fail validation.

    Returns:
        A ValidModels transformer bound to the concrete model type T.

    Raises:
        ValueError: If no model is registered for the given dataset file.
    """
    return ModelLoader(
        model=model,
        only_published=only_published,
        skip_validation_failures=skip_validation_failures,
    )


def get_dataset_file_for_model[T: SdeDatasetRecord](
    model: type[T],
) -> SdeDatasetFiles:
    """Get the corresponding SDE dataset file for a given model.

    Args:
        model: The pydantic model class to look up.

    Returns:
        The SdeDatasetFiles entry associated with the given model.

    Raises:
        ValueError: If no dataset file is registered for the given model.
    """
    dataset_file = REVERSE.get(model.__name__, None)
    if dataset_file is None:
        raise ValueError(f"No dataset file found for model: {model}")
    return dataset_file


def read_records[T: SdeDatasetRecord](
    sde_path: Path, model: type[T], only_published: bool, skip_validation_failures: bool
) -> Iterator[tuple[int, T | None]]:
    """Read typed records from the SDE dataset file for a given model.

    Args:
        sde_path: Path to the root SDE directory.
        model: The pydantic model class used to parse each record.
        only_published: Whether to only include published records.
        skip_validation_failures: Whether to skip records that fail validation.

    Yields:
        Tuples of (line_number, parsed_record_or_none) for each JSONL line.

    Raises:
        ValueError: If no dataset file is registered for the given model.
    """
    dataset_file = get_dataset_file_for_model(model)
    transformer = get_transformer(
        model,
        only_published=only_published,
        skip_validation_failures=skip_validation_failures,
    )
    file_path = sde_path / dataset_file.as_jsonl()
    return read_jsonl_file(file_path, transformer)
