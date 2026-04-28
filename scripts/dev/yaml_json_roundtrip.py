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

from eve_static_data.models import yaml_datasets

app = typer.Typer()

YAML_DATASET_CASES: list[tuple[str, type[RootModel[Any]]]] = [
    ("agentsInSpace.yaml", yaml_datasets.AgentsInSpaceRoot),
    ("agentTypes.yaml", yaml_datasets.AgentTypesRoot),
    ("ancestries.yaml", yaml_datasets.AncestriesRoot),
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


@app.command()
def main(
    sde_path: Annotated[Path, typer.Argument(..., help="Path to the SDE directory")],
    output_path: Annotated[
        Path, typer.Argument(..., help="Path to output the JSON files to")
    ],
) -> None:
    """Script to test YAML fixture round-tripping through JSON."""
    for sde_file, root_model in yaml_datasets.files_to_root_model_lookup().items():
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
