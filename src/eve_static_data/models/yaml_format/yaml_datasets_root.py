"""Pydantic models for YAML datasets."""

import logging
from typing import Any

from pydantic import RootModel

from eve_static_data.models.dataset_filenames import SdeDatasets
from eve_static_data.models.yaml_format import yaml_records

logger = logging.getLogger(__name__)

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
TypeListsRoot = RootModel[dict[int, yaml_records.TypeLists]]
TypeMaterialsRoot = RootModel[dict[int, yaml_records.TypeMaterials]]
EveTypesRoot = RootModel[dict[int, yaml_records.EveTypes]]


_dataset_to_root_model_map: dict[SdeDatasets, type[RootModel[Any]]] = {
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


def get_root_model_for_dataset(dataset: SdeDatasets) -> type[RootModel[Any]]:
    """Get the root model class for a given dataset."""
    return _dataset_to_root_model_map[dataset]


# Check that all datasets have a corresponding root model
for dataset in SdeDatasets:
    if dataset not in _dataset_to_root_model_map:
        logger.warning(
            f"No root model registered for dataset '{dataset}'. This may cause issues when loading records."
        )
