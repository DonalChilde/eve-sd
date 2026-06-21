"""Tests for YAML fixture validation against yaml_records root models."""

import importlib.resources
from importlib.resources.abc import Traversable
from typing import Any

import pytest
import yaml
from pydantic import RootModel

from eve_static_data.models.yaml_format import yaml_datasets_dc


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
    ("agentsInSpace.yaml", yaml_datasets_dc.AgentsInSpaceRoot),
    ("agentTypes.yaml", yaml_datasets_dc.AgentTypesRoot),
    ("ancestries.yaml", yaml_datasets_dc.AncestriesRoot),
    ("archetypes.yaml", yaml_datasets_dc.ArchetypesRoot),
    ("bloodlines.yaml", yaml_datasets_dc.BloodlinesRoot),
    ("blueprints.yaml", yaml_datasets_dc.BlueprintsRoot),
    ("categories.yaml", yaml_datasets_dc.CategoriesRoot),
    ("certificates.yaml", yaml_datasets_dc.CertificatesRoot),
    ("characterAttributes.yaml", yaml_datasets_dc.CharacterAttributesRoot),
    ("cloneGrades.yaml", yaml_datasets_dc.CloneGradesRoot),
    ("compressibleTypes.yaml", yaml_datasets_dc.CompressibleTypesRoot),
    ("contrabandTypes.yaml", yaml_datasets_dc.ContrabandTypesRoot),
    ("controlTowerResources.yaml", yaml_datasets_dc.ControlTowerResourcesRoot),
    ("corporationActivities.yaml", yaml_datasets_dc.CorporationActivitiesRoot),
    ("dbuffCollections.yaml", yaml_datasets_dc.DbuffCollectionsRoot),
    ("dogmaAttributeCategories.yaml", yaml_datasets_dc.DogmaAttributeCategoriesRoot),
    ("dogmaAttributes.yaml", yaml_datasets_dc.DogmaAttributesRoot),
    ("dogmaEffects.yaml", yaml_datasets_dc.DogmaEffectsRoot),
    ("dogmaUnits.yaml", yaml_datasets_dc.DogmaUnitsRoot),
    ("dungeons.yaml", yaml_datasets_dc.DungeonsRoot),
    ("dynamicItemAttributes.yaml", yaml_datasets_dc.DynamicItemAttributesRoot),
    ("factions.yaml", yaml_datasets_dc.FactionsRoot),
    ("freelanceJobSchemas.yaml", yaml_datasets_dc.FreelanceJobSchemasRoot),
    ("graphics.yaml", yaml_datasets_dc.GraphicsRoot),
    ("groups.yaml", yaml_datasets_dc.GroupsRoot),
    ("icons.yaml", yaml_datasets_dc.IconsRoot),
    ("landmarks.yaml", yaml_datasets_dc.LandmarksRoot),
    ("mapAsteroidBelts.yaml", yaml_datasets_dc.MapAsteroidBeltsRoot),
    ("mapConstellations.yaml", yaml_datasets_dc.MapConstellationsRoot),
    ("mapMoons.yaml", yaml_datasets_dc.MapMoonsRoot),
    ("mapPlanets.yaml", yaml_datasets_dc.MapPlanetsRoot),
    ("mapRegions.yaml", yaml_datasets_dc.MapRegionsRoot),
    ("mapSecondarySuns.yaml", yaml_datasets_dc.MapSecondarySunsRoot),
    ("mapSolarSystems.yaml", yaml_datasets_dc.MapSolarSystemsRoot),
    ("mapStargates.yaml", yaml_datasets_dc.MapStargatesRoot),
    ("mapStars.yaml", yaml_datasets_dc.MapStarsRoot),
    ("marketGroups.yaml", yaml_datasets_dc.MarketGroupsRoot),
    ("masteries.yaml", yaml_datasets_dc.MasteriesRoot),
    ("metaGroups.yaml", yaml_datasets_dc.MetaGroupsRoot),
    (
        "mercenaryTacticalOperations.yaml",
        yaml_datasets_dc.MercenaryTacticalOperationsRoot,
    ),
    ("npcCharacters.yaml", yaml_datasets_dc.NpcCharactersRoot),
    ("npcCorporationDivisions.yaml", yaml_datasets_dc.NpcCorporationDivisionsRoot),
    ("npcCorporations.yaml", yaml_datasets_dc.NpcCorporationsRoot),
    ("npcStations.yaml", yaml_datasets_dc.NpcStationsRoot),
    ("planetResources.yaml", yaml_datasets_dc.PlanetResourcesRoot),
    ("planetSchematics.yaml", yaml_datasets_dc.PlanetSchematicsRoot),
    ("races.yaml", yaml_datasets_dc.RacesRoot),
    ("skinLicenses.yaml", yaml_datasets_dc.SkinLicensesRoot),
    ("skinMaterials.yaml", yaml_datasets_dc.SkinMaterialsRoot),
    ("skins.yaml", yaml_datasets_dc.SkinsRoot),
    ("_sde.yaml", yaml_datasets_dc.SdeInfoRoot),
    ("sovereigntyUpgrades.yaml", yaml_datasets_dc.SovereigntyUpgradesRoot),
    ("stationOperations.yaml", yaml_datasets_dc.StationOperationsRoot),
    ("stationServices.yaml", yaml_datasets_dc.StationServicesRoot),
    ("translationLanguages.yaml", yaml_datasets_dc.TranslationLanguagesRoot),
    ("typeBonus.yaml", yaml_datasets_dc.TypeBonusRoot),
    ("typeDogma.yaml", yaml_datasets_dc.TypeDogmaRoot),
    ("typeLists.yaml", yaml_datasets_dc.TypeListsRoot),
    ("typeMaterials.yaml", yaml_datasets_dc.TypeMaterialsRoot),
    ("types.yaml", yaml_datasets_dc.EveTypesRoot),
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
