"""Pydantic models for YAML datasets."""

from typing import Any

from pydantic import RootModel

from eve_static_data.models import yaml_records
from eve_static_data.models.dataset_filenames import SdeDatasetFiles

AgentsInSpaceRoot = RootModel[dict[int, yaml_records.AgentsInSpace]]
AgentTypesRoot = RootModel[dict[int, yaml_records.AgentTypes]]
AncestriesRoot = RootModel[dict[int, yaml_records.Ancestries]]
ArchetypesRoot = RootModel[dict[int, yaml_records.Archetypes]]
BloodlinesRoot = RootModel[dict[int, yaml_records.Bloodlines]]
BlueprintsRoot = RootModel[dict[int, yaml_records.Blueprints]]
CategoriesRoot = RootModel[dict[int, yaml_records.Categories]]
CertificatesRoot = RootModel[dict[int, yaml_records.Certificates]]
CharacterAttributesRoot = RootModel[dict[int, yaml_records.CharacterAttributes]]
CloneGradesRoot = RootModel[dict[int, yaml_records.CloneGrades]]
CompressibleTypesRoot = RootModel[dict[int, yaml_records.CompressibleTypes]]
ContrabandTypesRoot = RootModel[dict[int, yaml_records.ContrabandTypes]]
ControlTowerResourcesRoot = RootModel[dict[int, yaml_records.ControlTowerResources]]
CorporationActivitiesRoot = RootModel[dict[int, yaml_records.CorporationActivities]]
DbuffCollectionsRoot = RootModel[dict[int, yaml_records.DbuffCollections]]
DogmaAttributeCategoriesRoot = RootModel[
    dict[int, yaml_records.DogmaAttributeCategories]
]
DogmaAttributesRoot = RootModel[dict[int, yaml_records.DogmaAttributes]]
DogmaEffectsRoot = RootModel[dict[int, yaml_records.DogmaEffects]]
DogmaUnitsRoot = RootModel[dict[int, yaml_records.DogmaUnits]]
DungeonsRoot = RootModel[dict[int, yaml_records.Dungeons]]
DynamicItemAttributesRoot = RootModel[dict[int, yaml_records.DynamicItemAttributes]]
FactionsRoot = RootModel[dict[int, yaml_records.Factions]]
FreelanceJobSchemasRoot = RootModel[dict[int, yaml_records.FreelanceJobSchemas]]
GraphicsRoot = RootModel[dict[int, yaml_records.Graphics]]
GroupsRoot = RootModel[dict[int, yaml_records.Groups]]
IconsRoot = RootModel[dict[int, yaml_records.Icons]]
LandmarksRoot = RootModel[dict[int, yaml_records.Landmarks]]
MapAsteroidBeltsRoot = RootModel[dict[int, yaml_records.MapAsteroidBelts]]
MapConstellationsRoot = RootModel[dict[int, yaml_records.MapConstellations]]
MapMoonsRoot = RootModel[dict[int, yaml_records.MapMoons]]
MapPlanetsRoot = RootModel[dict[int, yaml_records.MapPlanets]]
MapRegionsRoot = RootModel[dict[int, yaml_records.MapRegions]]
MapSecondarySunsRoot = RootModel[dict[int, yaml_records.MapSecondarySuns]]
MapSolarSystemsRoot = RootModel[dict[int, yaml_records.MapSolarSystems]]
MapStargatesRoot = RootModel[dict[int, yaml_records.MapStargates]]
MapStarsRoot = RootModel[dict[int, yaml_records.MapStars]]
MarketGroupsRoot = RootModel[dict[int, yaml_records.MarketGroups]]
MasteriesRoot = RootModel[dict[int, yaml_records.Masteries]]
MetaGroupsRoot = RootModel[dict[int, yaml_records.MetaGroups]]
MercenaryTacticalOperationsRoot = RootModel[
    dict[int, yaml_records.MercenaryTacticalOperations]
]
NpcCharactersRoot = RootModel[dict[int, yaml_records.NpcCharacters]]
NpcCorporationDivisionsRoot = RootModel[dict[int, yaml_records.NpcCorporationDivisions]]
NpcCorporationsRoot = RootModel[dict[int, yaml_records.NpcCorporations]]
NpcStationsRoot = RootModel[dict[int, yaml_records.NpcStations]]
PlanetResourcesRoot = RootModel[dict[int, yaml_records.PlanetResources]]
PlanetSchematicsRoot = RootModel[dict[int, yaml_records.PlanetSchematics]]
RacesRoot = RootModel[dict[int, yaml_records.Races]]
SdeInfoRoot = RootModel[dict[str, yaml_records.SdeInfo]]
SkinLicensesRoot = RootModel[dict[int, yaml_records.SkinLicenses]]
SkinMaterialsRoot = RootModel[dict[int, yaml_records.SkinMaterials]]
SkinsRoot = RootModel[dict[int, yaml_records.Skins]]
SovereigntyUpgradesRoot = RootModel[dict[int, yaml_records.SovereigntyUpgrades]]
StationOperationsRoot = RootModel[dict[int, yaml_records.StationOperations]]
StationServicesRoot = RootModel[dict[int, yaml_records.StationServices]]
TranslationLanguagesRoot = RootModel[dict[str, yaml_records.TranslationLanguages]]
TypeBonusRoot = RootModel[dict[int, yaml_records.TypeBonus]]
TypeDogmaRoot = RootModel[dict[int, yaml_records.TypeDogma]]
TypeMaterialsRoot = RootModel[dict[int, yaml_records.TypeMaterials]]
EveTypesRoot = RootModel[dict[int, yaml_records.EveTypes]]


def files_to_root_model_lookup() -> dict[SdeDatasetFiles, type[RootModel[Any]]]:
    """Get a lookup of SDE dataset files to their corresponding RootModel classes."""
    return {
        SdeDatasetFiles.AGENTS_IN_SPACE: AgentsInSpaceRoot,
        SdeDatasetFiles.AGENT_TYPES: AgentTypesRoot,
        SdeDatasetFiles.ANCESTRIES: AncestriesRoot,
        SdeDatasetFiles.ARCHETYPES: ArchetypesRoot,
        SdeDatasetFiles.BLOODLINES: BloodlinesRoot,
        SdeDatasetFiles.BLUEPRINTS: BlueprintsRoot,
        SdeDatasetFiles.CATEGORIES: CategoriesRoot,
        SdeDatasetFiles.CERTIFICATES: CertificatesRoot,
        SdeDatasetFiles.CHARACTER_ATTRIBUTES: CharacterAttributesRoot,
        SdeDatasetFiles.CLONE_GRADES: CloneGradesRoot,
        SdeDatasetFiles.COMPRESSIBLE_TYPES: CompressibleTypesRoot,
        SdeDatasetFiles.CONTRABAND_TYPES: ContrabandTypesRoot,
        SdeDatasetFiles.CONTROL_TOWER_RESOURCES: ControlTowerResourcesRoot,
        SdeDatasetFiles.CORPORATION_ACTIVITIES: CorporationActivitiesRoot,
        SdeDatasetFiles.DBUFF_COLLECTIONS: DbuffCollectionsRoot,
        SdeDatasetFiles.DOGMA_ATTRIBUTE_CATEGORIES: DogmaAttributeCategoriesRoot,
        SdeDatasetFiles.DOGMA_ATTRIBUTES: DogmaAttributesRoot,
        SdeDatasetFiles.DOGMA_EFFECTS: DogmaEffectsRoot,
        SdeDatasetFiles.DOGMA_UNITS: DogmaUnitsRoot,
        SdeDatasetFiles.DUNGEONS: DungeonsRoot,
        SdeDatasetFiles.DYNAMIC_ITEM_ATTRIBUTES: DynamicItemAttributesRoot,
        SdeDatasetFiles.FACTIONS: FactionsRoot,
        SdeDatasetFiles.FREELANCE_JOB_SCHEMAS: FreelanceJobSchemasRoot,
        SdeDatasetFiles.GRAPHICS: GraphicsRoot,
        SdeDatasetFiles.GROUPS: GroupsRoot,
        SdeDatasetFiles.ICONS: IconsRoot,
        SdeDatasetFiles.LANDMARKS: LandmarksRoot,
        SdeDatasetFiles.MAP_ASTEROID_BELTS: MapAsteroidBeltsRoot,
        SdeDatasetFiles.MAP_CONSTELLATIONS: MapConstellationsRoot,
        SdeDatasetFiles.MAP_MOONS: MapMoonsRoot,
        SdeDatasetFiles.MAP_PLANETS: MapPlanetsRoot,
        SdeDatasetFiles.MAP_REGIONS: MapRegionsRoot,
        SdeDatasetFiles.MAP_SECONDARY_SUNS: MapSecondarySunsRoot,
        SdeDatasetFiles.MAP_SOLAR_SYSTEMS: MapSolarSystemsRoot,
        SdeDatasetFiles.MAP_STARGATES: MapStargatesRoot,
        SdeDatasetFiles.MAP_STARS: MapStarsRoot,
        SdeDatasetFiles.MARKET_GROUPS: MarketGroupsRoot,
        SdeDatasetFiles.MASTERIES: MasteriesRoot,
        SdeDatasetFiles.META_GROUPS: MetaGroupsRoot,
        SdeDatasetFiles.MERCENARY_TACTICAL_OPERATIONS: MercenaryTacticalOperationsRoot,
        SdeDatasetFiles.NPC_CHARACTERS: NpcCharactersRoot,
        SdeDatasetFiles.NPC_CORPORATION_DIVISIONS: NpcCorporationDivisionsRoot,
        SdeDatasetFiles.NPC_CORPORATIONS: NpcCorporationsRoot,
        SdeDatasetFiles.NPC_STATIONS: NpcStationsRoot,
        SdeDatasetFiles.PLANET_RESOURCES: PlanetResourcesRoot,
        SdeDatasetFiles.PLANET_SCHEMATICS: PlanetSchematicsRoot,
        SdeDatasetFiles.RACES: RacesRoot,
        SdeDatasetFiles.SDE_INFO: SdeInfoRoot,
        SdeDatasetFiles.SKIN_LICENSES: SkinLicensesRoot,
        SdeDatasetFiles.SKIN_MATERIALS: SkinMaterialsRoot,
        SdeDatasetFiles.SKINS: SkinsRoot,
        SdeDatasetFiles.SOVEREIGNTY_UPGRADES: SovereigntyUpgradesRoot,
        SdeDatasetFiles.STATION_OPERATIONS: StationOperationsRoot,
        SdeDatasetFiles.STATION_SERVICES: StationServicesRoot,
        SdeDatasetFiles.TRANSLATION_LANGUAGES: TranslationLanguagesRoot,
        SdeDatasetFiles.TYPE_BONUS: TypeBonusRoot,
        SdeDatasetFiles.TYPE_DOGMA: TypeDogmaRoot,
        SdeDatasetFiles.TYPE_MATERIALS: TypeMaterialsRoot,
        SdeDatasetFiles.TYPES: EveTypesRoot,
    }
