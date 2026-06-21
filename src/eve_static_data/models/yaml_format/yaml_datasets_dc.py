"""Pydantic models for YAML datasets."""

from typing import Any

from pydantic import RootModel

from eve_static_data.models.dataset_filenames import SdeDatasets
from eve_static_data.models.yaml_format import yaml_records_dc

AgentsInSpaceRoot = RootModel[dict[int, yaml_records_dc.AgentsInSpace]]
AgentTypesRoot = RootModel[dict[int, yaml_records_dc.AgentTypes]]
AncestriesRoot = RootModel[dict[int, yaml_records_dc.Ancestries]]
ArchetypesRoot = RootModel[dict[int, yaml_records_dc.Archetypes]]
BloodlinesRoot = RootModel[dict[int, yaml_records_dc.Bloodlines]]
BlueprintsRoot = RootModel[dict[int, yaml_records_dc.Blueprints]]
CategoriesRoot = RootModel[dict[int, yaml_records_dc.Categories]]
CertificatesRoot = RootModel[dict[int, yaml_records_dc.Certificates]]
CharacterAttributesRoot = RootModel[dict[int, yaml_records_dc.CharacterAttributes]]
CloneGradesRoot = RootModel[dict[int, yaml_records_dc.CloneGrades]]
CompressibleTypesRoot = RootModel[dict[int, yaml_records_dc.CompressibleTypes]]
ContrabandTypesRoot = RootModel[dict[int, yaml_records_dc.ContrabandTypes]]
ControlTowerResourcesRoot = RootModel[dict[int, yaml_records_dc.ControlTowerResources]]
CorporationActivitiesRoot = RootModel[dict[int, yaml_records_dc.CorporationActivities]]
DbuffCollectionsRoot = RootModel[dict[int, yaml_records_dc.DbuffCollections]]
DogmaAttributeCategoriesRoot = RootModel[
    dict[int, yaml_records_dc.DogmaAttributeCategories]
]
DogmaAttributesRoot = RootModel[dict[int, yaml_records_dc.DogmaAttributes]]
DogmaEffectsRoot = RootModel[dict[int, yaml_records_dc.DogmaEffects]]
DogmaUnitsRoot = RootModel[dict[int, yaml_records_dc.DogmaUnits]]
DungeonsRoot = RootModel[dict[int, yaml_records_dc.Dungeons]]
DynamicItemAttributesRoot = RootModel[dict[int, yaml_records_dc.DynamicItemAttributes]]
FactionsRoot = RootModel[dict[int, yaml_records_dc.Factions]]
FreelanceJobSchemasRoot = RootModel[dict[int, yaml_records_dc.FreelanceJobSchemas]]
GraphicsRoot = RootModel[dict[int, yaml_records_dc.Graphics]]
GroupsRoot = RootModel[dict[int, yaml_records_dc.Groups]]
IconsRoot = RootModel[dict[int, yaml_records_dc.Icons]]
LandmarksRoot = RootModel[dict[int, yaml_records_dc.Landmarks]]
MapAsteroidBeltsRoot = RootModel[dict[int, yaml_records_dc.MapAsteroidBelts]]
MapConstellationsRoot = RootModel[dict[int, yaml_records_dc.MapConstellations]]
MapMoonsRoot = RootModel[dict[int, yaml_records_dc.MapMoons]]
MapPlanetsRoot = RootModel[dict[int, yaml_records_dc.MapPlanets]]
MapRegionsRoot = RootModel[dict[int, yaml_records_dc.MapRegions]]
MapSecondarySunsRoot = RootModel[dict[int, yaml_records_dc.MapSecondarySuns]]
MapSolarSystemsRoot = RootModel[dict[int, yaml_records_dc.MapSolarSystems]]
MapStargatesRoot = RootModel[dict[int, yaml_records_dc.MapStargates]]
MapStarsRoot = RootModel[dict[int, yaml_records_dc.MapStars]]
MarketGroupsRoot = RootModel[dict[int, yaml_records_dc.MarketGroups]]
MasteriesRoot = RootModel[dict[int, yaml_records_dc.Masteries]]
MetaGroupsRoot = RootModel[dict[int, yaml_records_dc.MetaGroups]]
MercenaryTacticalOperationsRoot = RootModel[
    dict[int, yaml_records_dc.MercenaryTacticalOperations]
]
NpcCharactersRoot = RootModel[dict[int, yaml_records_dc.NpcCharacters]]
NpcCorporationDivisionsRoot = RootModel[
    dict[int, yaml_records_dc.NpcCorporationDivisions]
]
NpcCorporationsRoot = RootModel[dict[int, yaml_records_dc.NpcCorporations]]
NpcStationsRoot = RootModel[dict[int, yaml_records_dc.NpcStations]]
PlanetResourcesRoot = RootModel[dict[int, yaml_records_dc.PlanetResources]]
PlanetSchematicsRoot = RootModel[dict[int, yaml_records_dc.PlanetSchematics]]
RacesRoot = RootModel[dict[int, yaml_records_dc.Races]]
SdeInfoRoot = RootModel[dict[str, yaml_records_dc.SdeInfo]]
SkinLicensesRoot = RootModel[dict[int, yaml_records_dc.SkinLicenses]]
SkinMaterialsRoot = RootModel[dict[int, yaml_records_dc.SkinMaterials]]
SkinsRoot = RootModel[dict[int, yaml_records_dc.Skins]]
SovereigntyUpgradesRoot = RootModel[dict[int, yaml_records_dc.SovereigntyUpgrades]]
StationOperationsRoot = RootModel[dict[int, yaml_records_dc.StationOperations]]
StationServicesRoot = RootModel[dict[int, yaml_records_dc.StationServices]]
TranslationLanguagesRoot = RootModel[dict[str, yaml_records_dc.TranslationLanguages]]
TypeBonusRoot = RootModel[dict[int, yaml_records_dc.TypeBonus]]
TypeDogmaRoot = RootModel[dict[int, yaml_records_dc.TypeDogma]]
TypeListsRoot = RootModel[dict[int, yaml_records_dc.TypeLists]]
TypeMaterialsRoot = RootModel[dict[int, yaml_records_dc.TypeMaterials]]
EveTypesRoot = RootModel[dict[int, yaml_records_dc.EveTypes]]


def datasets_to_root_model_lookup() -> dict[SdeDatasets, type[RootModel[Any]]]:
    """Get a lookup of SDE dataset files to their corresponding RootModel classes."""
    return {
        SdeDatasets.AGENTS_IN_SPACE: AgentsInSpaceRoot,
        SdeDatasets.AGENT_TYPES: AgentTypesRoot,
        SdeDatasets.ANCESTRIES: AncestriesRoot,
        SdeDatasets.ARCHETYPES: ArchetypesRoot,
        SdeDatasets.BLOODLINES: BloodlinesRoot,
        SdeDatasets.BLUEPRINTS: BlueprintsRoot,
        SdeDatasets.CATEGORIES: CategoriesRoot,
        SdeDatasets.CERTIFICATES: CertificatesRoot,
        SdeDatasets.CHARACTER_ATTRIBUTES: CharacterAttributesRoot,
        SdeDatasets.CLONE_GRADES: CloneGradesRoot,
        SdeDatasets.COMPRESSIBLE_TYPES: CompressibleTypesRoot,
        SdeDatasets.CONTRABAND_TYPES: ContrabandTypesRoot,
        SdeDatasets.CONTROL_TOWER_RESOURCES: ControlTowerResourcesRoot,
        SdeDatasets.CORPORATION_ACTIVITIES: CorporationActivitiesRoot,
        SdeDatasets.DBUFF_COLLECTIONS: DbuffCollectionsRoot,
        SdeDatasets.DOGMA_ATTRIBUTE_CATEGORIES: DogmaAttributeCategoriesRoot,
        SdeDatasets.DOGMA_ATTRIBUTES: DogmaAttributesRoot,
        SdeDatasets.DOGMA_EFFECTS: DogmaEffectsRoot,
        SdeDatasets.DOGMA_UNITS: DogmaUnitsRoot,
        SdeDatasets.DUNGEONS: DungeonsRoot,
        SdeDatasets.DYNAMIC_ITEM_ATTRIBUTES: DynamicItemAttributesRoot,
        SdeDatasets.FACTIONS: FactionsRoot,
        SdeDatasets.FREELANCE_JOB_SCHEMAS: FreelanceJobSchemasRoot,
        SdeDatasets.GRAPHICS: GraphicsRoot,
        SdeDatasets.GROUPS: GroupsRoot,
        SdeDatasets.ICONS: IconsRoot,
        SdeDatasets.LANDMARKS: LandmarksRoot,
        SdeDatasets.MAP_ASTEROID_BELTS: MapAsteroidBeltsRoot,
        SdeDatasets.MAP_CONSTELLATIONS: MapConstellationsRoot,
        SdeDatasets.MAP_MOONS: MapMoonsRoot,
        SdeDatasets.MAP_PLANETS: MapPlanetsRoot,
        SdeDatasets.MAP_REGIONS: MapRegionsRoot,
        SdeDatasets.MAP_SECONDARY_SUNS: MapSecondarySunsRoot,
        SdeDatasets.MAP_SOLAR_SYSTEMS: MapSolarSystemsRoot,
        SdeDatasets.MAP_STARGATES: MapStargatesRoot,
        SdeDatasets.MAP_STARS: MapStarsRoot,
        SdeDatasets.MARKET_GROUPS: MarketGroupsRoot,
        SdeDatasets.MASTERIES: MasteriesRoot,
        SdeDatasets.META_GROUPS: MetaGroupsRoot,
        SdeDatasets.MERCENARY_TACTICAL_OPERATIONS: MercenaryTacticalOperationsRoot,
        SdeDatasets.NPC_CHARACTERS: NpcCharactersRoot,
        SdeDatasets.NPC_CORPORATION_DIVISIONS: NpcCorporationDivisionsRoot,
        SdeDatasets.NPC_CORPORATIONS: NpcCorporationsRoot,
        SdeDatasets.NPC_STATIONS: NpcStationsRoot,
        SdeDatasets.PLANET_RESOURCES: PlanetResourcesRoot,
        SdeDatasets.PLANET_SCHEMATICS: PlanetSchematicsRoot,
        SdeDatasets.RACES: RacesRoot,
        SdeDatasets.SDE_INFO: SdeInfoRoot,
        SdeDatasets.SKIN_LICENSES: SkinLicensesRoot,
        SdeDatasets.SKIN_MATERIALS: SkinMaterialsRoot,
        SdeDatasets.SKINS: SkinsRoot,
        SdeDatasets.SOVEREIGNTY_UPGRADES: SovereigntyUpgradesRoot,
        SdeDatasets.STATION_OPERATIONS: StationOperationsRoot,
        SdeDatasets.STATION_SERVICES: StationServicesRoot,
        SdeDatasets.TRANSLATION_LANGUAGES: TranslationLanguagesRoot,
        SdeDatasets.TYPE_BONUS: TypeBonusRoot,
        SdeDatasets.TYPE_DOGMA: TypeDogmaRoot,
        SdeDatasets.TYPE_MATERIALS: TypeMaterialsRoot,
        SdeDatasets.TYPE_LISTS: TypeListsRoot,
        SdeDatasets.TYPES: EveTypesRoot,
    }
