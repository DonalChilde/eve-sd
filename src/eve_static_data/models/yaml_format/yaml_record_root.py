# """Root models for SDE dataset records in YAML format."""

# import logging
# from typing import Any

# from pydantic import RootModel

# from eve_static_data.models.common import DatasetRecordBase
# from eve_static_data.models.dataset_filenames import SdeDatasets
# from eve_static_data.models.yaml_format import yaml_records

# logger = logging.getLogger(__name__)

# AgentsInSpaceRecordRoot = RootModel[yaml_records.AgentsInSpaceRecord]
# AgentTypesRecordRoot = RootModel[yaml_records.AgentTypesRecord]
# AncestriesRecordRoot = RootModel[yaml_records.AncestriesRecord]
# ArchetypesRecordRoot = RootModel[yaml_records.ArchetypesRecord]
# BloodlinesRecordRoot = RootModel[yaml_records.BloodlinesRecord]
# BlueprintsRecordRoot = RootModel[yaml_records.BlueprintsRecord]
# CategoriesRecordRoot = RootModel[yaml_records.CategoriesRecord]
# CertificatesRecordRoot = RootModel[yaml_records.CertificatesRecord]
# CharacterAttributesRecordRoot = RootModel[yaml_records.CharacterAttributesRecord]
# CharacterTitlesRecordRoot = RootModel[yaml_records.CharacterTitlesRecord]
# CloneGradesRecordRoot = RootModel[yaml_records.CloneGradesRecord]
# CompressibleTypesRecordRoot = RootModel[yaml_records.CompressibleTypesRecord]
# ContrabandTypesRecordRoot = RootModel[yaml_records.ContrabandTypesRecord]
# ControlTowerResourcesRecordRoot = RootModel[yaml_records.ControlTowerResourcesRecord]
# CorporationActivitiesRecordRoot = RootModel[yaml_records.CorporationActivitiesRecord]
# DbuffCollectionsRecordRoot = RootModel[yaml_records.DbuffCollectionsRecord]
# DogmaAttributeCategoriesRecordRoot = RootModel[
#     yaml_records.DogmaAttributeCategoriesRecord
# ]
# DogmaAttributesRecordRoot = RootModel[yaml_records.DogmaAttributesRecord]
# DogmaEffectsRecordRoot = RootModel[yaml_records.DogmaEffectsRecord]
# DogmaUnitsRecordRoot = RootModel[yaml_records.DogmaUnitsRecord]
# DungeonsRecordRoot = RootModel[yaml_records.DungeonsRecord]
# DynamicItemAttributesRecordRoot = RootModel[yaml_records.DynamicItemAttributesRecord]

# FactionsRecordRoot = RootModel[yaml_records.FactionsRecord]
# FreelanceJobSchemasRecordRoot = RootModel[yaml_records.FreelanceJobSchemasRecord]

# GraphicsRecordRoot = RootModel[yaml_records.GraphicsRecord]
# GroupsRecordRoot = RootModel[yaml_records.GroupsRecord]
# IconsRecordRoot = RootModel[yaml_records.IconsRecord]
# LandmarksRecordRoot = RootModel[yaml_records.LandmarksRecord]
# MapAsteroidBeltsRecordRoot = RootModel[yaml_records.MapAsteroidBeltsRecord]
# MapConstellationsRecordRoot = RootModel[yaml_records.MapConstellationsRecord]
# MapMoonsRecordRoot = RootModel[yaml_records.MapMoonsRecord]
# MapPlanetsRecordRoot = RootModel[yaml_records.MapPlanetsRecord]
# MapRegionsRecordRoot = RootModel[yaml_records.MapRegionsRecord]
# MapSecondarySunsRecordRoot = RootModel[yaml_records.MapSecondarySunsRecord]
# MapSolarSystemsRecordRoot = RootModel[yaml_records.MapSolarSystemsRecord]
# MapStargatesRecordRoot = RootModel[yaml_records.MapStargatesRecord]
# MapStarsRecordRoot = RootModel[yaml_records.MapStarsRecord]
# MarketGroupsRecordRoot = RootModel[yaml_records.MarketGroupsRecord]
# MasteriesRecordRoot = RootModel[yaml_records.MasteriesRecord]
# MetaGroupsRecordRoot = RootModel[yaml_records.MetaGroupsRecord]
# MercenaryTacticalOperationsRecordRoot = RootModel[
#     yaml_records.MercenaryTacticalOperationsRecord
# ]


# NpcCharactersRecordRoot = RootModel[yaml_records.NpcCharactersRecord]
# NpcCorporationDivisionsRecordRoot = RootModel[
#     yaml_records.NpcCorporationDivisionsRecord
# ]

# NpcCorporationsRecordRoot = RootModel[yaml_records.NpcCorporationsRecord]
# NpcStationsRecordRoot = RootModel[yaml_records.NpcStationsRecord]
# PlanetResourcesRecordRoot = RootModel[yaml_records.PlanetResourcesRecord]
# PlanetSchematicsRecordRoot = RootModel[yaml_records.PlanetSchematicsRecord]
# RacesRecordRoot = RootModel[yaml_records.RacesRecord]
# SdeInfoRecordRoot = RootModel[yaml_records.SdeInfoRecord]
# SkinLicensesRecordRoot = RootModel[yaml_records.SkinLicensesRecord]
# SkinMaterialsRecordRoot = RootModel[yaml_records.SkinMaterialsRecord]
# SkinsRecordRoot = RootModel[yaml_records.SkinsRecord]
# SovereigntyUpgradesRecordRoot = RootModel[yaml_records.SovereigntyUpgradesRecord]

# StationOperationsRecordRoot = RootModel[yaml_records.StationOperationsRecord]
# StationServicesRecordRoot = RootModel[yaml_records.StationServicesRecord]
# TranslationLanguagesRecordRoot = RootModel[yaml_records.TranslationLanguagesRecord]

# TypeBonusRecordRoot = RootModel[yaml_records.TypeBonusRecord]
# TypeDogmaRecordRoot = RootModel[yaml_records.TypeDogmaRecord]
# TypeListsRecordRoot = RootModel[yaml_records.TypeListsRecord]
# TypeMaterialsRecordRoot = RootModel[yaml_records.TypeMaterialsRecord]
# EveTypesRecordRoot = RootModel[yaml_records.EveTypesRecord]

# _dataset_to_root_model_map: dict[SdeDatasets, type[RootModel[Any]]] = {
#     SdeDatasets.AGENTS_IN_SPACE: AgentsInSpaceRecordRoot,
#     SdeDatasets.AGENT_TYPES: AgentTypesRecordRoot,
#     SdeDatasets.ANCESTRIES: AncestriesRecordRoot,
#     SdeDatasets.ARCHETYPES: ArchetypesRecordRoot,
#     SdeDatasets.BLOODLINES: BloodlinesRecordRoot,
#     SdeDatasets.BLUEPRINTS: BlueprintsRecordRoot,
#     SdeDatasets.CATEGORIES: CategoriesRecordRoot,
#     SdeDatasets.CERTIFICATES: CertificatesRecordRoot,
#     SdeDatasets.CHARACTER_ATTRIBUTES: CharacterAttributesRecordRoot,
#     SdeDatasets.CHARACTER_TITLES: CharacterTitlesRecordRoot,
#     SdeDatasets.CLONE_GRADES: CloneGradesRecordRoot,
#     SdeDatasets.COMPRESSIBLE_TYPES: CompressibleTypesRecordRoot,
#     SdeDatasets.CONTRABAND_TYPES: ContrabandTypesRecordRoot,
#     SdeDatasets.CONTROL_TOWER_RESOURCES: ControlTowerResourcesRecordRoot,
#     SdeDatasets.CORPORATION_ACTIVITIES: CorporationActivitiesRecordRoot,
#     SdeDatasets.DBUFF_COLLECTIONS: DbuffCollectionsRecordRoot,
#     SdeDatasets.DOGMA_ATTRIBUTE_CATEGORIES: DogmaAttributeCategoriesRecordRoot,
#     SdeDatasets.DOGMA_ATTRIBUTES: DogmaAttributesRecordRoot,
#     SdeDatasets.DOGMA_EFFECTS: DogmaEffectsRecordRoot,
#     SdeDatasets.DOGMA_UNITS: DogmaUnitsRecordRoot,
#     SdeDatasets.DUNGEONS: DungeonsRecordRoot,
#     SdeDatasets.DYNAMIC_ITEM_ATTRIBUTES: DynamicItemAttributesRecordRoot,
#     SdeDatasets.FACTIONS: FactionsRecordRoot,
#     SdeDatasets.FREELANCE_JOB_SCHEMAS: FreelanceJobSchemasRecordRoot,
#     SdeDatasets.GRAPHICS: GraphicsRecordRoot,
#     SdeDatasets.GROUPS: GroupsRecordRoot,
#     SdeDatasets.ICONS: IconsRecordRoot,
#     SdeDatasets.LANDMARKS: LandmarksRecordRoot,
#     SdeDatasets.MAP_ASTEROID_BELTS: MapAsteroidBeltsRecordRoot,
#     SdeDatasets.MAP_CONSTELLATIONS: MapConstellationsRecordRoot,
#     SdeDatasets.MAP_MOONS: MapMoonsRecordRoot,
#     SdeDatasets.MAP_PLANETS: MapPlanetsRecordRoot,
#     SdeDatasets.MAP_REGIONS: MapRegionsRecordRoot,
#     SdeDatasets.MAP_SECONDARY_SUNS: MapSecondarySunsRecordRoot,
#     SdeDatasets.MAP_SOLAR_SYSTEMS: MapSolarSystemsRecordRoot,
#     SdeDatasets.MAP_STARGATES: MapStargatesRecordRoot,
#     SdeDatasets.MAP_STARS: MapStarsRecordRoot,
#     SdeDatasets.MARKET_GROUPS: MarketGroupsRecordRoot,
#     SdeDatasets.MASTERIES: MasteriesRecordRoot,
#     SdeDatasets.META_GROUPS: MetaGroupsRecordRoot,
#     SdeDatasets.MERCENARY_TACTICAL_OPERATIONS: MercenaryTacticalOperationsRecordRoot,
#     SdeDatasets.NPC_CHARACTERS: NpcCharactersRecordRoot,
#     SdeDatasets.NPC_CORPORATION_DIVISIONS: NpcCorporationDivisionsRecordRoot,
#     SdeDatasets.NPC_CORPORATIONS: NpcCorporationsRecordRoot,
#     SdeDatasets.NPC_STATIONS: NpcStationsRecordRoot,
#     SdeDatasets.PLANET_RESOURCES: PlanetResourcesRecordRoot,
#     SdeDatasets.PLANET_SCHEMATICS: PlanetSchematicsRecordRoot,
#     SdeDatasets.RACES: RacesRecordRoot,
#     SdeDatasets.SDE_INFO: SdeInfoRecordRoot,
#     SdeDatasets.SKIN_LICENSES: SkinLicensesRecordRoot,
#     SdeDatasets.SKIN_MATERIALS: SkinMaterialsRecordRoot,
#     SdeDatasets.SKINS: SkinsRecordRoot,
#     SdeDatasets.SOVEREIGNTY_UPGRADES: SovereigntyUpgradesRecordRoot,
#     SdeDatasets.STATION_OPERATIONS: StationOperationsRecordRoot,
#     SdeDatasets.STATION_SERVICES: StationServicesRecordRoot,
#     SdeDatasets.TRANSLATION_LANGUAGES: TranslationLanguagesRecordRoot,
#     SdeDatasets.TYPE_BONUS: TypeBonusRecordRoot,
#     SdeDatasets.TYPE_DOGMA: TypeDogmaRecordRoot,
#     SdeDatasets.TYPE_LISTS: TypeListsRecordRoot,
#     SdeDatasets.TYPE_MATERIALS: TypeMaterialsRecordRoot,
#     SdeDatasets.TYPES: EveTypesRecordRoot,
# }


# def get_record_root_model_for_dataset(dataset: SdeDatasets) -> type[RootModel[Any]]:
#     """Get the root model class for a given dataset."""
#     if dataset not in _dataset_to_root_model_map:
#         raise ValueError(f"No root model registered for dataset '{dataset}'.")
#     return _dataset_to_root_model_map[dataset]


# def get_root_model_for_record[R: DatasetRecordBase](
#     record_model: type[R],
# ) -> RootModel[R]:
#     """Get the root model for a given record model."""
#     # This could also be done as a dynamic map, but this is more explicit.
#     dataset = record_model.dataset
#     if dataset not in _dataset_to_root_model_map:
#         raise ValueError(f"No root model registered for dataset '{dataset}'.")
#     root_model = _dataset_to_root_model_map[dataset]
#     return root_model  # type: ignore


# # check that all datasets have a corresponding record root model
# for dataset in SdeDatasets:
#     if dataset not in _dataset_to_root_model_map:
#         logger.warning(
#             f"No record root model registered for dataset '{dataset}'. This may cause issues when loading records."
#         )
