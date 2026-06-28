# """Tests for YAML fixture validation against yaml_records root models."""

# import importlib.resources
# from importlib.resources.abc import Traversable
# from typing import Any

# import pytest
# import yaml
# from pydantic import RootModel

# from eve_static_data.models.yaml_format import yaml_datasets_root


# def _yaml_fixture_path(file_name: str) -> Traversable:
#     """Get a Traversable to a YAML SDE fixture file.

#     Args:
#         file_name: Name of the fixture file under tests/resources/sde_data/yaml.

#     Returns:
#         Traversable to the fixture file.
#     """
#     return importlib.resources.files("tests.resources.sde_data.yaml") / file_name


# def _load_yaml_mapping(file_name: str) -> dict[Any, Any]:
#     """Load a YAML fixture expected to have a dictionary root.

#     Args:
#         file_name: Name of the fixture file under tests/resources/sde_data/yaml.

#     Returns:
#         Parsed YAML mapping.
#     """
#     fixture_path = _yaml_fixture_path(file_name)
#     with fixture_path.open(encoding="utf-8") as file_handle:
#         # TODO use yaml loader functi
#         loaded: Any = yaml.safe_load(file_handle)

#     assert isinstance(loaded, dict)
#     return loaded  # type: ignore


# # Add new dataset/model pairs here as yaml_records.py grows.
# YAML_DATASET_CASES: list[tuple[str, type[RootModel[Any]]]] = [
#     ("agentsInSpace.yaml", yaml_datasets_root.AgentsInSpaceRoot),
#     ("agentTypes.yaml", yaml_datasets_root.AgentTypesRoot),
#     ("ancestries.yaml", yaml_datasets_root.AncestriesRoot),
#     ("archetypes.yaml", yaml_datasets_root.ArchetypesRoot),
#     ("bloodlines.yaml", yaml_datasets_root.BloodlinesRoot),
#     ("blueprints.yaml", yaml_datasets_root.BlueprintsRoot),
#     ("categories.yaml", yaml_datasets_root.CategoriesRoot),
#     ("certificates.yaml", yaml_datasets_root.CertificatesRoot),
#     ("characterAttributes.yaml", yaml_datasets_root.CharacterAttributesRoot),
#     ("cloneGrades.yaml", yaml_datasets_root.CloneGradesRoot),
#     ("compressibleTypes.yaml", yaml_datasets_root.CompressibleTypesRoot),
#     ("contrabandTypes.yaml", yaml_datasets_root.ContrabandTypesRoot),
#     ("controlTowerResources.yaml", yaml_datasets_root.ControlTowerResourcesRoot),
#     ("corporationActivities.yaml", yaml_datasets_root.CorporationActivitiesRoot),
#     ("dbuffCollections.yaml", yaml_datasets_root.DbuffCollectionsRoot),
#     ("dogmaAttributeCategories.yaml", yaml_datasets_root.DogmaAttributeCategoriesRoot),
#     ("dogmaAttributes.yaml", yaml_datasets_root.DogmaAttributesRoot),
#     ("dogmaEffects.yaml", yaml_datasets_root.DogmaEffectsRoot),
#     ("dogmaUnits.yaml", yaml_datasets_root.DogmaUnitsRoot),
#     ("dungeons.yaml", yaml_datasets_root.DungeonsRoot),
#     ("dynamicItemAttributes.yaml", yaml_datasets_root.DynamicItemAttributesRoot),
#     ("factions.yaml", yaml_datasets_root.FactionsRoot),
#     ("freelanceJobSchemas.yaml", yaml_datasets_root.FreelanceJobSchemasRoot),
#     ("graphics.yaml", yaml_datasets_root.GraphicsRoot),
#     ("groups.yaml", yaml_datasets_root.GroupsRoot),
#     ("icons.yaml", yaml_datasets_root.IconsRoot),
#     ("landmarks.yaml", yaml_datasets_root.LandmarksRoot),
#     ("mapAsteroidBelts.yaml", yaml_datasets_root.MapAsteroidBeltsRoot),
#     ("mapConstellations.yaml", yaml_datasets_root.MapConstellationsRoot),
#     ("mapMoons.yaml", yaml_datasets_root.MapMoonsRoot),
#     ("mapPlanets.yaml", yaml_datasets_root.MapPlanetsRoot),
#     ("mapRegions.yaml", yaml_datasets_root.MapRegionsRoot),
#     ("mapSecondarySuns.yaml", yaml_datasets_root.MapSecondarySunsRoot),
#     ("mapSolarSystems.yaml", yaml_datasets_root.MapSolarSystemsRoot),
#     ("mapStargates.yaml", yaml_datasets_root.MapStargatesRoot),
#     ("mapStars.yaml", yaml_datasets_root.MapStarsRoot),
#     ("marketGroups.yaml", yaml_datasets_root.MarketGroupsRoot),
#     ("masteries.yaml", yaml_datasets_root.MasteriesRoot),
#     ("metaGroups.yaml", yaml_datasets_root.MetaGroupsRoot),
#     (
#         "mercenaryTacticalOperations.yaml",
#         yaml_datasets_root.MercenaryTacticalOperationsRoot,
#     ),
#     ("npcCharacters.yaml", yaml_datasets_root.NpcCharactersRoot),
#     ("npcCorporationDivisions.yaml", yaml_datasets_root.NpcCorporationDivisionsRoot),
#     ("npcCorporations.yaml", yaml_datasets_root.NpcCorporationsRoot),
#     ("npcStations.yaml", yaml_datasets_root.NpcStationsRoot),
#     ("planetResources.yaml", yaml_datasets_root.PlanetResourcesRoot),
#     ("planetSchematics.yaml", yaml_datasets_root.PlanetSchematicsRoot),
#     ("races.yaml", yaml_datasets_root.RacesRoot),
#     ("skinLicenses.yaml", yaml_datasets_root.SkinLicensesRoot),
#     ("skinMaterials.yaml", yaml_datasets_root.SkinMaterialsRoot),
#     ("skins.yaml", yaml_datasets_root.SkinsRoot),
#     ("_sde.yaml", yaml_datasets_root.SdeInfoRoot),
#     ("sovereigntyUpgrades.yaml", yaml_datasets_root.SovereigntyUpgradesRoot),
#     ("stationOperations.yaml", yaml_datasets_root.StationOperationsRoot),
#     ("stationServices.yaml", yaml_datasets_root.StationServicesRoot),
#     ("translationLanguages.yaml", yaml_datasets_root.TranslationLanguagesRoot),
#     ("typeBonus.yaml", yaml_datasets_root.TypeBonusRoot),
#     ("typeDogma.yaml", yaml_datasets_root.TypeDogmaRoot),
#     ("typeLists.yaml", yaml_datasets_root.TypeListsRoot),
#     ("typeMaterials.yaml", yaml_datasets_root.TypeMaterialsRoot),
#     ("types.yaml", yaml_datasets_root.EveTypesRoot),
# ]


# @pytest.mark.parametrize(
#     ("fixture_file_name", "root_model"),
#     YAML_DATASET_CASES,
# )
# def test_yaml_fixtures_validate_against_root_models(
#     fixture_file_name: str,
#     root_model: type[RootModel[Any]],
# ) -> None:
#     """YAML fixture mappings should validate against their root models."""
#     payload = _load_yaml_mapping(fixture_file_name)

#     validated = root_model.model_validate(payload)

#     assert isinstance(validated, root_model)
#     assert validated.model_dump(mode="python")
