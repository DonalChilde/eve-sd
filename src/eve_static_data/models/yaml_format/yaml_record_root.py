"""Root models for SDE dataset records in YAML format."""

import logging
from typing import Any

from pydantic import RootModel

from eve_static_data.models.common import DatasetRecordBase
from eve_static_data.models.dataset_filenames import SdeDatasets
from eve_static_data.models.yaml_format import yaml_records

logger = logging.getLogger(__name__)

AgentsInSpaceRecordRoot = RootModel[yaml_records.AgentsInSpace]
AgentTypesRecordRoot = RootModel[yaml_records.AgentTypes]
AncestriesRecordRoot = RootModel[yaml_records.Ancestries]
ArchetypesRecordRoot = RootModel[yaml_records.Archetypes]
BloodlinesRecordRoot = RootModel[yaml_records.Bloodlines]
BlueprintsRecordRoot = RootModel[yaml_records.Blueprints]
CategoriesRecordRoot = RootModel[yaml_records.Categories]
CertificatesRecordRoot = RootModel[yaml_records.Certificates]
CharacterAttributesRecordRoot = RootModel[yaml_records.CharacterAttributes]
CloneGradesRecordRoot = RootModel[yaml_records.CloneGrades]
CompressibleTypesRecordRoot = RootModel[yaml_records.CompressibleTypes]
ContrabandTypesRecordRoot = RootModel[yaml_records.ContrabandTypes]
ControlTowerResourcesRecordRoot = RootModel[yaml_records.ControlTowerResources]
CorporationActivitiesRecordRoot = RootModel[yaml_records.CorporationActivities]
DbuffCollectionsRecordRoot = RootModel[yaml_records.DbuffCollections]
DogmaAttributeCategoriesRecordRoot = RootModel[yaml_records.DogmaAttributeCategories]
DogmaAttributesRecordRoot = RootModel[yaml_records.DogmaAttributes]
DogmaEffectsRecordRoot = RootModel[yaml_records.DogmaEffects]
DogmaUnitsRecordRoot = RootModel[yaml_records.DogmaUnits]
DungeonsRecordRoot = RootModel[yaml_records.Dungeons]
DynamicItemAttributesRecordRoot = RootModel[yaml_records.DynamicItemAttributes]

FactionsRecordRoot = RootModel[yaml_records.Factions]
FreelanceJobSchemasRecordRoot = RootModel[yaml_records.FreelanceJobSchemas]

GraphicsRecordRoot = RootModel[yaml_records.Graphics]
GroupsRecordRoot = RootModel[yaml_records.Groups]
IconsRecordRoot = RootModel[yaml_records.Icons]
LandmarksRecordRoot = RootModel[yaml_records.Landmarks]
MapAsteroidBeltsRecordRoot = RootModel[yaml_records.MapAsteroidBelts]
MapConstellationsRecordRoot = RootModel[yaml_records.MapConstellations]
MapMoonsRecordRoot = RootModel[yaml_records.MapMoons]
MapPlanetsRecordRoot = RootModel[yaml_records.MapPlanets]
MapRegionsRecordRoot = RootModel[yaml_records.MapRegions]
MapSecondarySunsRecordRoot = RootModel[yaml_records.MapSecondarySuns]
MapSolarSystemsRecordRoot = RootModel[yaml_records.MapSolarSystems]
MapStargatesRecordRoot = RootModel[yaml_records.MapStargates]
MapStarsRecordRoot = RootModel[yaml_records.MapStars]
MarketGroupsRecordRoot = RootModel[yaml_records.MarketGroups]
MasteriesRecordRoot = RootModel[yaml_records.Masteries]
MetaGroupsRecordRoot = RootModel[yaml_records.MetaGroups]
MercenaryTacticalOperationsRecordRoot = RootModel[
    yaml_records.MercenaryTacticalOperations
]


NpcCharactersRecordRoot = RootModel[yaml_records.NpcCharacters]
NpcCorporationDivisionsRecordRoot = RootModel[yaml_records.NpcCorporationDivisions]

NpcCorporationsRecordRoot = RootModel[yaml_records.NpcCorporations]
NpcStationsRecordRoot = RootModel[yaml_records.NpcStations]
PlanetResourcesRecordRoot = RootModel[yaml_records.PlanetResources]
PlanetSchematicsRecordRoot = RootModel[yaml_records.PlanetSchematics]
RacesRecordRoot = RootModel[yaml_records.Races]
SdeInfoRecordRoot = RootModel[yaml_records.SdeInfo]
SkinLicensesRecordRoot = RootModel[yaml_records.SkinLicenses]
SkinMaterialsRecordRoot = RootModel[yaml_records.SkinMaterials]
SkinsRecordRoot = RootModel[yaml_records.Skins]
SovereigntyUpgradesRecordRoot = RootModel[yaml_records.SovereigntyUpgrades]

StationOperationsRecordRoot = RootModel[yaml_records.StationOperations]
StationServicesRecordRoot = RootModel[yaml_records.StationServices]
TranslationLanguagesRecordRoot = RootModel[yaml_records.TranslationLanguages]

TypeBonusRecordRoot = RootModel[yaml_records.TypeBonus]
TypeDogmaRecordRoot = RootModel[yaml_records.TypeDogma]
TypeListsRecordRoot = RootModel[yaml_records.TypeLists]
TypeMaterialsRecordRoot = RootModel[yaml_records.TypeMaterials]
EveTypesRecordRoot = RootModel[yaml_records.EveTypes]

_dataset_to_root_model_map: dict[SdeDatasets, type[RootModel[Any]]] = {
    SdeDatasets.AGENTS_IN_SPACE: AgentsInSpaceRecordRoot,
    SdeDatasets.AGENT_TYPES: AgentTypesRecordRoot,
    SdeDatasets.ANCESTRIES: AncestriesRecordRoot,
    SdeDatasets.ARCHETYPES: ArchetypesRecordRoot,
    SdeDatasets.BLOODLINES: BloodlinesRecordRoot,
    SdeDatasets.BLUEPRINTS: BlueprintsRecordRoot,
    SdeDatasets.CATEGORIES: CategoriesRecordRoot,
    SdeDatasets.CERTIFICATES: CertificatesRecordRoot,
    SdeDatasets.CHARACTER_ATTRIBUTES: CharacterAttributesRecordRoot,
    SdeDatasets.CLONE_GRADES: CloneGradesRecordRoot,
    SdeDatasets.COMPRESSIBLE_TYPES: CompressibleTypesRecordRoot,
    SdeDatasets.CONTRABAND_TYPES: ContrabandTypesRecordRoot,
    SdeDatasets.CONTROL_TOWER_RESOURCES: ControlTowerResourcesRecordRoot,
    SdeDatasets.CORPORATION_ACTIVITIES: CorporationActivitiesRecordRoot,
    SdeDatasets.DBUFF_COLLECTIONS: DbuffCollectionsRecordRoot,
    SdeDatasets.DOGMA_ATTRIBUTE_CATEGORIES: DogmaAttributeCategoriesRecordRoot,
    SdeDatasets.DOGMA_ATTRIBUTES: DogmaAttributesRecordRoot,
    SdeDatasets.DOGMA_EFFECTS: DogmaEffectsRecordRoot,
    SdeDatasets.DOGMA_UNITS: DogmaUnitsRecordRoot,
    SdeDatasets.DUNGEONS: DungeonsRecordRoot,
    SdeDatasets.DYNAMIC_ITEM_ATTRIBUTES: DynamicItemAttributesRecordRoot,
    SdeDatasets.FACTIONS: FactionsRecordRoot,
    SdeDatasets.FREELANCE_JOB_SCHEMAS: FreelanceJobSchemasRecordRoot,
    SdeDatasets.GRAPHICS: GraphicsRecordRoot,
    SdeDatasets.GROUPS: GroupsRecordRoot,
    SdeDatasets.ICONS: IconsRecordRoot,
    SdeDatasets.LANDMARKS: LandmarksRecordRoot,
    SdeDatasets.MAP_ASTEROID_BELTS: MapAsteroidBeltsRecordRoot,
    SdeDatasets.MAP_CONSTELLATIONS: MapConstellationsRecordRoot,
    SdeDatasets.MAP_MOONS: MapMoonsRecordRoot,
    SdeDatasets.MAP_PLANETS: MapPlanetsRecordRoot,
    SdeDatasets.MAP_REGIONS: MapRegionsRecordRoot,
    SdeDatasets.MAP_SECONDARY_SUNS: MapSecondarySunsRecordRoot,
    SdeDatasets.MAP_SOLAR_SYSTEMS: MapSolarSystemsRecordRoot,
    SdeDatasets.MAP_STARGATES: MapStargatesRecordRoot,
    SdeDatasets.MAP_STARS: MapStarsRecordRoot,
    SdeDatasets.MARKET_GROUPS: MarketGroupsRecordRoot,
    SdeDatasets.MASTERIES: MasteriesRecordRoot,
    SdeDatasets.META_GROUPS: MetaGroupsRecordRoot,
    SdeDatasets.MERCENARY_TACTICAL_OPERATIONS: MercenaryTacticalOperationsRecordRoot,
    SdeDatasets.NPC_CHARACTERS: NpcCharactersRecordRoot,
    SdeDatasets.NPC_CORPORATION_DIVISIONS: NpcCorporationDivisionsRecordRoot,
    SdeDatasets.NPC_CORPORATIONS: NpcCorporationsRecordRoot,
    SdeDatasets.NPC_STATIONS: NpcStationsRecordRoot,
    SdeDatasets.PLANET_RESOURCES: PlanetResourcesRecordRoot,
    SdeDatasets.PLANET_SCHEMATICS: PlanetSchematicsRecordRoot,
    SdeDatasets.RACES: RacesRecordRoot,
    SdeDatasets.SDE_INFO: SdeInfoRecordRoot,
    SdeDatasets.SKIN_LICENSES: SkinLicensesRecordRoot,
    SdeDatasets.SKIN_MATERIALS: SkinMaterialsRecordRoot,
    SdeDatasets.SKINS: SkinsRecordRoot,
    SdeDatasets.SOVEREIGNTY_UPGRADES: SovereigntyUpgradesRecordRoot,
    SdeDatasets.STATION_OPERATIONS: StationOperationsRecordRoot,
    SdeDatasets.STATION_SERVICES: StationServicesRecordRoot,
    SdeDatasets.TRANSLATION_LANGUAGES: TranslationLanguagesRecordRoot,
    SdeDatasets.TYPE_BONUS: TypeBonusRecordRoot,
    SdeDatasets.TYPE_DOGMA: TypeDogmaRecordRoot,
    SdeDatasets.TYPE_LISTS: TypeListsRecordRoot,
    SdeDatasets.TYPE_MATERIALS: TypeMaterialsRecordRoot,
    SdeDatasets.TYPES: EveTypesRecordRoot,
}


def get_record_root_model_for_dataset(dataset: SdeDatasets) -> type[RootModel[Any]]:
    """Get the root model class for a given dataset."""
    if dataset not in _dataset_to_root_model_map:
        raise ValueError(f"No root model registered for dataset '{dataset}'.")
    return _dataset_to_root_model_map[dataset]


def get_root_model_for_record[R: DatasetRecordBase](
    record_model: type[R],
) -> RootModel[R]:
    """Get the root model for a given record model."""
    # This could also be done as a dynamic map, but this is more explicit.
    dataset = record_model.dataset
    if dataset not in _dataset_to_root_model_map:
        raise ValueError(f"No root model registered for dataset '{dataset}'.")
    root_model = _dataset_to_root_model_map[dataset]
    return root_model  # type: ignore


# check that all datasets have a corresponding record root model
for dataset in SdeDatasets:
    if dataset not in _dataset_to_root_model_map:
        logger.warning(
            f"No record root model registered for dataset '{dataset}'. This may cause issues when loading records."
        )
