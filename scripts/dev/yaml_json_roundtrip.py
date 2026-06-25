# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "pydantic>=2.12.5",
#     "pyyaml>=6.0.3",
#     "typer>=0.24.1",
# ]
# ///
import json
from pathlib import Path
from time import perf_counter
from typing import Annotated, Any

import typer
from pydantic import RootModel
from yaml import safe_load

from eve_static_data.models.yaml_format import yaml_datasets_root

app = typer.Typer()

YAML_DATASET_CASES: list[tuple[str, type[RootModel[Any]]]] = [
    ("agentsInSpace.yaml", yaml_datasets_root.AgentsInSpaceRoot),
    ("agentTypes.yaml", yaml_datasets_root.AgentTypesRoot),
    ("ancestries.yaml", yaml_datasets_root.AncestriesRoot),
    ("bloodlines.yaml", yaml_datasets_root.BloodlinesRoot),
    ("blueprints.yaml", yaml_datasets_root.BlueprintsRoot),
    ("categories.yaml", yaml_datasets_root.CategoriesRoot),
    ("certificates.yaml", yaml_datasets_root.CertificatesRoot),
    ("characterAttributes.yaml", yaml_datasets_root.CharacterAttributesRoot),
    ("cloneGrades.yaml", yaml_datasets_root.CloneGradesRoot),
    ("compressibleTypes.yaml", yaml_datasets_root.CompressibleTypesRoot),
    ("contrabandTypes.yaml", yaml_datasets_root.ContrabandTypesRoot),
    ("controlTowerResources.yaml", yaml_datasets_root.ControlTowerResourcesRoot),
    ("corporationActivities.yaml", yaml_datasets_root.CorporationActivitiesRoot),
    ("dbuffCollections.yaml", yaml_datasets_root.DbuffCollectionsRoot),
    ("dogmaAttributeCategories.yaml", yaml_datasets_root.DogmaAttributeCategoriesRoot),
    ("dogmaAttributes.yaml", yaml_datasets_root.DogmaAttributesRoot),
    ("dogmaEffects.yaml", yaml_datasets_root.DogmaEffectsRoot),
    ("dogmaUnits.yaml", yaml_datasets_root.DogmaUnitsRoot),
    ("dynamicItemAttributes.yaml", yaml_datasets_root.DynamicItemAttributesRoot),
    ("factions.yaml", yaml_datasets_root.FactionsRoot),
    ("freelanceJobSchemas.yaml", yaml_datasets_root.FreelanceJobSchemasRoot),
    ("graphics.yaml", yaml_datasets_root.GraphicsRoot),
    ("groups.yaml", yaml_datasets_root.GroupsRoot),
    ("icons.yaml", yaml_datasets_root.IconsRoot),
    ("landmarks.yaml", yaml_datasets_root.LandmarksRoot),
    ("mapAsteroidBelts.yaml", yaml_datasets_root.MapAsteroidBeltsRoot),
    ("mapConstellations.yaml", yaml_datasets_root.MapConstellationsRoot),
    ("mapMoons.yaml", yaml_datasets_root.MapMoonsRoot),
    ("mapPlanets.yaml", yaml_datasets_root.MapPlanetsRoot),
    ("mapRegions.yaml", yaml_datasets_root.MapRegionsRoot),
    ("mapSecondarySuns.yaml", yaml_datasets_root.MapSecondarySunsRoot),
    ("mapSolarSystems.yaml", yaml_datasets_root.MapSolarSystemsRoot),
    ("mapStargates.yaml", yaml_datasets_root.MapStargatesRoot),
    ("mapStars.yaml", yaml_datasets_root.MapStarsRoot),
    ("marketGroups.yaml", yaml_datasets_root.MarketGroupsRoot),
    ("masteries.yaml", yaml_datasets_root.MasteriesRoot),
    ("metaGroups.yaml", yaml_datasets_root.MetaGroupsRoot),
    (
        "mercenaryTacticalOperations.yaml",
        yaml_datasets_root.MercenaryTacticalOperationsRoot,
    ),
    ("npcCharacters.yaml", yaml_datasets_root.NpcCharactersRoot),
    ("npcCorporationDivisions.yaml", yaml_datasets_root.NpcCorporationDivisionsRoot),
    ("npcCorporations.yaml", yaml_datasets_root.NpcCorporationsRoot),
    ("npcStations.yaml", yaml_datasets_root.NpcStationsRoot),
    ("planetResources.yaml", yaml_datasets_root.PlanetResourcesRoot),
    ("planetSchematics.yaml", yaml_datasets_root.PlanetSchematicsRoot),
    ("races.yaml", yaml_datasets_root.RacesRoot),
    ("skinLicenses.yaml", yaml_datasets_root.SkinLicensesRoot),
    ("skinMaterials.yaml", yaml_datasets_root.SkinMaterialsRoot),
    ("skins.yaml", yaml_datasets_root.SkinsRoot),
    ("_sde.yaml", yaml_datasets_root.SdeInfoRoot),
    ("sovereigntyUpgrades.yaml", yaml_datasets_root.SovereigntyUpgradesRoot),
    ("stationOperations.yaml", yaml_datasets_root.StationOperationsRoot),
    ("stationServices.yaml", yaml_datasets_root.StationServicesRoot),
    ("translationLanguages.yaml", yaml_datasets_root.TranslationLanguagesRoot),
    ("typeBonus.yaml", yaml_datasets_root.TypeBonusRoot),
    ("typeDogma.yaml", yaml_datasets_root.TypeDogmaRoot),
    ("typeMaterials.yaml", yaml_datasets_root.TypeMaterialsRoot),
    ("types.yaml", yaml_datasets_root.EveTypesRoot),
]


@app.command()
def main(
    sde_path: Annotated[Path, typer.Argument(..., help="Path to the SDE directory")],
    output_path: Annotated[
        Path, typer.Argument(..., help="Path to output the JSON files to")
    ],
) -> None:
    """Script to test YAML fixture round-tripping through JSON."""
    for (
        sde_file,
        root_model,
    ) in yaml_datasets_root.datasets_to_root_model_lookup().items():
        yaml_file_path = sde_path / sde_file.as_yaml()
        print(f"Processing {yaml_file_path}...")
        with yaml_file_path.open(encoding="utf-8") as file_handle:
            start = perf_counter()
            loaded: Any = safe_load(file_handle)
            print(
                f"\tLoaded {sde_file} with pyyaml in {perf_counter() - start:.2f} seconds, now validating against {root_model.__name__}..."
            )

        assert isinstance(loaded, dict)
        start = perf_counter()
        model_instance = root_model.model_validate(loaded)
        print(
            f"\tValidated {sde_file} against {root_model.__name__} in {perf_counter() - start:.2f} seconds, now dumping to JSON..."
        )
        json_output = model_instance.model_dump_json(indent=2)

        output_file_path = output_path / sde_file.as_json()
        output_file_path.parent.mkdir(parents=True, exist_ok=True)
        start = perf_counter()
        output_file_path.write_text(json_output, encoding="utf-8")
        print(
            f"\tDumped {sde_file} to JSON via pydantic in {perf_counter() - start:.2f} seconds at {output_file_path}."
        )
        start = perf_counter()
        with open(output_file_path, encoding="utf-8") as file_handle:
            reloaded = root_model.model_validate_json(file_handle.read())
        print(
            f"\tReloaded {sde_file} from JSON via pydantic in {perf_counter() - start:.2f} seconds."
        )
        start = perf_counter()
        with open(output_file_path, encoding="utf-8") as file_handle:
            reloaded_json = json.load(file_handle)
        print(
            f"\tReloaded {sde_file} from JSON using standard json.load in {perf_counter() - start:.2f} seconds, final validation successful."
        )


if __name__ == "__main__":
    app()
