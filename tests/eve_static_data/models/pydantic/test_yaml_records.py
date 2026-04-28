"""Tests for YAML fixture validation against yaml_records root models."""

import importlib.resources
from importlib.resources.abc import Traversable
from typing import Any

import pytest
import yaml
from pydantic import RootModel

from eve_static_data.models import yaml_datasets


def _yaml_fixture_path(file_name: str) -> Traversable:
    """Get a Traversable to a YAML SDE fixture file.

    Args:
        file_name: Name of the fixture file under tests/resources/sde_data/yaml.

    Returns:
        Traversable to the fixture file.
    """
    return importlib.resources.files("tests.resources.sde_data.yaml") / file_name


def _load_yaml_mapping(file_name: str) -> dict[Any, Any]:
    """Load a YAML fixture expected to have a dictionary root.

    Args:
        file_name: Name of the fixture file under tests/resources/sde_data/yaml.

    Returns:
        Parsed YAML mapping.
    """
    fixture_path = _yaml_fixture_path(file_name)
    with fixture_path.open(encoding="utf-8") as file_handle:
        loaded: Any = yaml.safe_load(file_handle)

    assert isinstance(loaded, dict)
    return loaded  # type: ignore


# Add new dataset/model pairs here as yaml_records.py grows.
YAML_DATASET_CASES: list[tuple[str, type[RootModel[Any]]]] = [
    ("agentsInSpace.yaml", yaml_datasets.AgentsInSpaceRoot),
    ("agentTypes.yaml", yaml_datasets.AgentTypesRoot),
    ("ancestries.yaml", yaml_datasets.AncestriesRoot),
    ("archetypes.yaml", yaml_datasets.ArchetypesRoot),
    ("bloodlines.yaml", yaml_datasets.BloodlinesRoot),
    ("blueprints.yaml", yaml_datasets.BlueprintsRoot),
    ("categories.yaml", yaml_datasets.CategoriesRoot),
    ("certificates.yaml", yaml_datasets.CertificatesRoot),
    ("characterAttributes.yaml", yaml_datasets.CharacterAttributesRoot),
    ("cloneGrades.yaml", yaml_datasets.CloneGradesRoot),
    ("compressibleTypes.yaml", yaml_datasets.CompressibleTypesRoot),
    ("contrabandTypes.yaml", yaml_datasets.ContrabandTypesRoot),
    ("controlTowerResources.yaml", yaml_datasets.ControlTowerResourcesRoot),
    ("corporationActivities.yaml", yaml_datasets.CorporationActivitiesRoot),
    ("dbuffCollections.yaml", yaml_datasets.DbuffCollectionsRoot),
    ("dogmaAttributeCategories.yaml", yaml_datasets.DogmaAttributeCategoriesRoot),
    ("dogmaAttributes.yaml", yaml_datasets.DogmaAttributesRoot),
    ("dogmaEffects.yaml", yaml_datasets.DogmaEffectsRoot),
    ("dogmaUnits.yaml", yaml_datasets.DogmaUnitsRoot),
    ("dungeons.yaml", yaml_datasets.DungeonsRoot),
    ("dynamicItemAttributes.yaml", yaml_datasets.DynamicItemAttributesRoot),
    ("factions.yaml", yaml_datasets.FactionsRoot),
    ("freelanceJobSchemas.yaml", yaml_datasets.FreelanceJobSchemasRoot),
    ("graphics.yaml", yaml_datasets.GraphicsRoot),
    ("groups.yaml", yaml_datasets.GroupsRoot),
    ("icons.yaml", yaml_datasets.IconsRoot),
    ("landmarks.yaml", yaml_datasets.LandmarksRoot),
    ("mapAsteroidBelts.yaml", yaml_datasets.MapAsteroidBeltsRoot),
    ("mapConstellations.yaml", yaml_datasets.MapConstellationsRoot),
    ("mapMoons.yaml", yaml_datasets.MapMoonsRoot),
    ("mapPlanets.yaml", yaml_datasets.MapPlanetsRoot),
    ("mapRegions.yaml", yaml_datasets.MapRegionsRoot),
    ("mapSecondarySuns.yaml", yaml_datasets.MapSecondarySunsRoot),
    ("mapSolarSystems.yaml", yaml_datasets.MapSolarSystemsRoot),
    ("mapStargates.yaml", yaml_datasets.MapStargatesRoot),
    ("mapStars.yaml", yaml_datasets.MapStarsRoot),
    ("marketGroups.yaml", yaml_datasets.MarketGroupsRoot),
    ("masteries.yaml", yaml_datasets.MasteriesRoot),
    ("metaGroups.yaml", yaml_datasets.MetaGroupsRoot),
    ("mercenaryTacticalOperations.yaml", yaml_datasets.MercenaryTacticalOperationsRoot),
    ("npcCharacters.yaml", yaml_datasets.NpcCharactersRoot),
    ("npcCorporationDivisions.yaml", yaml_datasets.NpcCorporationDivisionsRoot),
    ("npcCorporations.yaml", yaml_datasets.NpcCorporationsRoot),
    ("npcStations.yaml", yaml_datasets.NpcStationsRoot),
    ("planetResources.yaml", yaml_datasets.PlanetResourcesRoot),
    ("planetSchematics.yaml", yaml_datasets.PlanetSchematicsRoot),
    ("races.yaml", yaml_datasets.RacesRoot),
    ("skinLicenses.yaml", yaml_datasets.SkinLicensesRoot),
    ("skinMaterials.yaml", yaml_datasets.SkinMaterialsRoot),
    ("skins.yaml", yaml_datasets.SkinsRoot),
    ("_sde.yaml", yaml_datasets.SdeInfoRoot),
    ("sovereigntyUpgrades.yaml", yaml_datasets.SovereigntyUpgradesRoot),
    ("stationOperations.yaml", yaml_datasets.StationOperationsRoot),
    ("stationServices.yaml", yaml_datasets.StationServicesRoot),
    ("translationLanguages.yaml", yaml_datasets.TranslationLanguagesRoot),
    ("typeBonus.yaml", yaml_datasets.TypeBonusRoot),
    ("typeDogma.yaml", yaml_datasets.TypeDogmaRoot),
    ("typeMaterials.yaml", yaml_datasets.TypeMaterialsRoot),
    ("types.yaml", yaml_datasets.EveTypesRoot),
]


@pytest.mark.parametrize(
    ("fixture_file_name", "root_model"),
    YAML_DATASET_CASES,
)
def test_yaml_fixtures_validate_against_root_models(
    fixture_file_name: str,
    root_model: type[RootModel[Any]],
) -> None:
    """YAML fixture mappings should validate against their root models."""
    payload = _load_yaml_mapping(fixture_file_name)

    validated = root_model.model_validate(payload)

    assert isinstance(validated, root_model)
    assert validated.model_dump(mode="python")
