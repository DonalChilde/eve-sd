"""Pydantic models for YAML datasets."""

import logging
from typing import Any

from pydantic import RootModel

from eve_static_data.models.dataset_filenames import SdeDatasets
from eve_static_data.models.yaml_format import yaml_records

logger = logging.getLogger(__name__)

AgentsInSpaceRoot = RootModel[dict[int, yaml_records.AgentsInSpaceRecord]]
AgentTypesRoot = RootModel[dict[int, yaml_records.AgentTypesRecord]]
AncestriesRoot = RootModel[dict[int, yaml_records.AncestriesRecord]]
ArchetypesRoot = RootModel[dict[int, yaml_records.ArchetypesRecord]]
BloodlinesRoot = RootModel[dict[int, yaml_records.BloodlinesRecord]]
BlueprintsRoot = RootModel[dict[int, yaml_records.BlueprintsRecord]]
CategoriesRoot = RootModel[dict[int, yaml_records.CategoriesRecord]]
CertificatesRoot = RootModel[dict[int, yaml_records.CertificatesRecord]]
CharacterAttributesRoot = RootModel[dict[int, yaml_records.CharacterAttributesRecord]]
CloneGradesRoot = RootModel[dict[int, yaml_records.CloneGradesRecord]]
CompressibleTypesRoot = RootModel[dict[int, yaml_records.CompressibleTypesRecord]]
ContrabandTypesRoot = RootModel[dict[int, yaml_records.ContrabandTypesRecord]]
ControlTowerResourcesRoot = RootModel[
    dict[int, yaml_records.ControlTowerResourcesRecord]
]
CorporationActivitiesRoot = RootModel[
    dict[int, yaml_records.CorporationActivitiesRecord]
]
DbuffCollectionsRoot = RootModel[dict[int, yaml_records.DbuffCollectionsRecord]]
DogmaAttributeCategoriesRoot = RootModel[
    dict[int, yaml_records.DogmaAttributeCategoriesRecord]
]
DogmaAttributesRoot = RootModel[dict[int, yaml_records.DogmaAttributesRecord]]
DogmaEffectsRoot = RootModel[dict[int, yaml_records.DogmaEffectsRecord]]
DogmaUnitsRoot = RootModel[dict[int, yaml_records.DogmaUnitsRecord]]
DungeonsRoot = RootModel[dict[int, yaml_records.DungeonsRecord]]
DynamicItemAttributesRoot = RootModel[
    dict[int, yaml_records.DynamicItemAttributesRecord]
]
FactionsRoot = RootModel[dict[int, yaml_records.FactionsRecord]]
FreelanceJobSchemasRoot = RootModel[dict[int, yaml_records.FreelanceJobSchemas]]
GraphicsRoot = RootModel[dict[int, yaml_records.GraphicsRecord]]
GroupsRoot = RootModel[dict[int, yaml_records.GroupsRecord]]
IconsRoot = RootModel[dict[int, yaml_records.IconsRecord]]
LandmarksRoot = RootModel[dict[int, yaml_records.LandmarksRecord]]
MapAsteroidBeltsRoot = RootModel[dict[int, yaml_records.MapAsteroidBeltsRecord]]
MapConstellationsRoot = RootModel[dict[int, yaml_records.MapConstellationsRecord]]
MapMoonsRoot = RootModel[dict[int, yaml_records.MapMoonsRecord]]
MapPlanetsRoot = RootModel[dict[int, yaml_records.MapPlanetsRecord]]
MapRegionsRoot = RootModel[dict[int, yaml_records.MapRegionsRecord]]
MapSecondarySunsRoot = RootModel[dict[int, yaml_records.MapSecondarySunsRecord]]
MapSolarSystemsRoot = RootModel[dict[int, yaml_records.MapSolarSystemsRecord]]
MapStargatesRoot = RootModel[dict[int, yaml_records.MapStargatesRecord]]
MapStarsRoot = RootModel[dict[int, yaml_records.MapStarsRecord]]
MarketGroupsRoot = RootModel[dict[int, yaml_records.MarketGroupsRecord]]
MasteriesRoot = RootModel[dict[int, yaml_records.Masteries]]
MetaGroupsRoot = RootModel[dict[int, yaml_records.MetaGroupsRecord]]
MercenaryTacticalOperationsRoot = RootModel[
    dict[int, yaml_records.MercenaryTacticalOperationsRecord]
]
NpcCharactersRoot = RootModel[dict[int, yaml_records.NpcCharactersRecord]]
NpcCorporationDivisionsRoot = RootModel[
    dict[int, yaml_records.NpcCorporationDivisionsRecord]
]
NpcCorporationsRoot = RootModel[dict[int, yaml_records.NpcCorporationsRecord]]
NpcStationsRoot = RootModel[dict[int, yaml_records.NpcStationsRecord]]
PlanetResourcesRoot = RootModel[dict[int, yaml_records.PlanetResourcesRecord]]
PlanetSchematicsRoot = RootModel[dict[int, yaml_records.PlanetSchematicsRecord]]
RacesRoot = RootModel[dict[int, yaml_records.RacesRecord]]
SdeInfoRoot = RootModel[dict[str, yaml_records.SdeInfoRecord]]
SkinLicensesRoot = RootModel[dict[int, yaml_records.SkinLicensesRecord]]
SkinMaterialsRoot = RootModel[dict[int, yaml_records.SkinMaterialsRecord]]
SkinsRoot = RootModel[dict[int, yaml_records.SkinsRecord]]
SovereigntyUpgradesRoot = RootModel[dict[int, yaml_records.SovereigntyUpgradesRecord]]
StationOperationsRoot = RootModel[dict[int, yaml_records.StationOperationsRecord]]
StationServicesRoot = RootModel[dict[int, yaml_records.StationServicesRecord]]
TranslationLanguagesRoot = RootModel[dict[str, yaml_records.TranslationLanguagesRecord]]
TypeBonusRoot = RootModel[dict[int, yaml_records.TypeBonusRecord]]
TypeDogmaRoot = RootModel[dict[int, yaml_records.TypeDogmaRecord]]
TypeListsRoot = RootModel[dict[int, yaml_records.TypeListsRecord]]
TypeMaterialsRoot = RootModel[dict[int, yaml_records.TypeMaterialsRecord]]
EveTypesRoot = RootModel[dict[int, yaml_records.EveTypesRecord]]


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
